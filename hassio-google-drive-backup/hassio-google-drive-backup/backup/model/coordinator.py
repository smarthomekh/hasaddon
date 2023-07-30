from asyncio import CancelledError, Task, create_task, wait, Event
from datetime import timedelta
from threading import Lock
from typing import Dict, List

from injector import inject, singleton

from backup.config import Config, Setting, CreateOptions, DurationParser
from backup.exceptions import (KnownError, LogicError, NoBackup, PleaseWait,
                               UserCancelledError)
from backup.util import GlobalInfo, Backoff, Estimator
from backup.time import Time
from backup.worker import Trigger
from backup.logger import getLogger
from backup.creds.creds import Creds
from .precache import Precache
from .model import BackupSource, Model
from .backups import AbstractBackup, Backup, SOURCE_HA
from random import Random

logger = getLogger(__name__)


@singleton
class Coordinator(Trigger):
    @inject
    def __init__(self, model: Model, time: Time, config: Config, global_info: GlobalInfo, estimator: Estimator):
        super().__init__()
        self._model = model
        self._precache: Precache = None
        self._time = time
        self._config = config
        self._lock: Lock = Lock()
        self._global_info: GlobalInfo = global_info
        self._sources: Dict[str, BackupSource] = {
            self._model.source.name(): self._model.source,
            self._model.dest.name(): self._model.dest
        }
        self._backoff = Backoff(initial=0, base=10, max=config.get(Setting.MAX_BACKOFF_SECONDS))
        self._estimator = estimator
        self._busy = False
        self._sync_task: Task = None
        self._sync_start = Event()
        self._sync_wait = Event()
        self._sync_wait.set()
        self._random = Random()
        self._random.seed()
        self._next_sync_offset = self._random.random()
        self._global_info.triggerBackupCooldown(timedelta(minutes=self._config.get(Setting.BACKUP_STARTUP_DELAY_MINUTES)))
        self.trigger()

    def saveCreds(self, creds: Creds):
        if not self._model.dest.enabled():
            # Since this is the first time saving credentials (eg the addon was just enabled).  Hold off on
            # automatic backups for a few minutes to give the user a little while to figure out whats going on.
            self._global_info.triggerBackupCooldown(timedelta(minutes=self._config.get(Setting.BACKUP_STARTUP_DELAY_MINUTES)))

        self._model.dest.saveCreds(creds)
        self._global_info.credsSaved()

    def setPrecache(self, precache: Precache):
        self._precache = precache

    def name(self):
        return "Coordinator"

    def enabled(self) -> bool:
        return self._model.enabled()

    def isWaitingForStartup(self):
        return self._model.waiting_for_startup

    def ignoreStartupDelay(self):
        self._model.ignore_startup_delay = True

    async def check(self) -> bool:
        if self._time.now() >= self.nextSyncAttempt():
            self.reset()
            return True
        else:
            return await super().check()

    async def sync(self):
        await self._withSoftLock(lambda: self._sync_wrapper())

    def isSyncing(self):
        task = self._sync_task
        return task is not None and not task.done()

    def isWorkingThroughUpload(self):
        return self.isSyncing() and self._model.isWorkingThroughUpload()

    async def waitForSyncToFinish(self):
        task = self._sync_task
        if task is not None:
            await task

    async def cancel(self):
        task = self._sync_task
        if task is not None and not task.done():
            task.cancel()
            self.clearCaches()
            await wait([task])

    def nextSyncAttempt(self):
        if self._global_info._last_error is not None:
            # we had an error last
            failure = self._global_info._last_failure_time
            if failure is None:
                return self._time.now() - timedelta(minutes=1)
            return failure + timedelta(seconds=self._backoff.peek())
        else:
            scheduled = self._global_info._last_success
            if scheduled is None:
                scheduled = self._time.now() - timedelta(minutes=1)
            else:
                scheduled += timedelta(seconds=self.nextSyncCheckOffset())
            next_backup = self.nextBackupTime()
            if next_backup is None:
                return scheduled
            else:
                return min(self.nextBackupTime(), scheduled)

    def nextSyncCheckOffset(self):
        """Determines how long we shoudl wait from the last check the refresh the cache of backups from Google Drive and Home Assistant"""
        # If we always sync MAX_SYNC_INTERVAL_SECONDS secodns after the last
        # check, then the addon in aggregate puts a really high strain on google
        # on every hour and the addon's auth servers need to be provisioned for
        # a big peak, which is epxensive.  Instead we add some randomness to the time interval.
        randomness_max = self._config.get(Setting.MAX_SYNC_INTERVAL_SECONDS) * self._config.get(Setting.DEFAULT_SYNC_INTERVAL_VARIATION)
        non_randomness = self._config.get(Setting.MAX_SYNC_INTERVAL_SECONDS) - randomness_max

        # The offset should be stable between syncs, which gets controlled by updating _next_sync_offset on each good sync
        return self._next_sync_offset * randomness_max + non_randomness

    def nextBackupTime(self, include_pending=True):
        return self._buildModel().nextBackup(self._time.now(), include_pending)

    def buildBackupMetrics(self):
        info = {}
        for source in self._sources:
            source_class = self._sources[source]
            source_info = {
                'backups': 0,
                'retained': 0,
                'deletable': 0,
                'name': source,
                'title': source_class.title(),
                'latest': None,
                'max': source_class.maxCount(),
                'enabled': source_class.enabled(),
                'icon': source_class.icon(),
                'ignored': 0,
                'detail': source_class.detail()
            }
            size = 0
            ignored_size = 0
            latest = None
            for backup in self.backups():
                data: AbstractBackup = backup.getSource(source)
                if data is None:
                    continue
                if data.ignore() and backup.ignore():
                    source_info['ignored'] += 1
                if backup.ignore():
                    ignored_size += backup.size()
                    continue
                source_info['backups'] += 1
                if data.retained():
                    source_info['retained'] += 1
                else:
                    source_info['deletable'] += 1
                if latest is None or data.date() > latest:
                    latest = data.date()
                size += int(data.sizeInt())
            if latest is not None:
                source_info['latest'] = self._time.asRfc3339String(latest)
            source_info['size'] = Estimator.asSizeString(size)
            source_info['ignored_size'] = Estimator.asSizeString(ignored_size)
            free_space = source_class.freeSpace()
            if free_space is not None and source_class.needsSpaceCheck:
                source_info['free_space'] = Estimator.asSizeString(free_space)
            info[source] = source_info
        return info

    async def _sync_wrapper(self):
        self._sync_task = create_task(
            self._sync(), name="Internal sync worker")
        await wait([self._sync_task])

    async def _sync(self):
        try:
            self._sync_start.set()
            await self._sync_wait.wait()
            logger.info("Syncing Backups")
            self._global_info.sync()
            self._estimator.refresh()
            await self._buildModel().sync(self._time.now())
            self._next_sync_offset = self._random.random()
            self._global_info.success()
            self._backoff.reset()
            self._global_info.setSkipSpaceCheckOnce(False)
        except BaseException as e:
            self.handleError(e)
        finally:
            if self._precache:
                # Any sync should invalidate the precache regardless of the outcome
                # so the next sync uses fresh data
                self.clearCaches()
            self._updateFreshness()

    def handleError(self, e):
        if isinstance(e, CancelledError):
            e = UserCancelledError()
        if isinstance(e, KnownError):
            known: KnownError = e
            logger.error(known.message())
            if known.retrySoon():
                self._backoff.backoff(e)
            else:
                self._backoff.maxOut()
        else:
            logger.printException(e)
            self._backoff.backoff(e)
        self._global_info.failed(e)

        text = DurationParser().format(timedelta(seconds=self._backoff.peek()))
        logger.info("I'll try again in {0}".format(text))

    def backups(self) -> List[Backup]:
        ret = list(self._model.backups.values())
        ret.sort(key=lambda s: s.date())
        return ret

    async def uploadBackups(self, slug):
        await self._withSoftLock(lambda: self._uploadBackup(slug))

    async def _uploadBackup(self, slug):
        self.clearCaches()
        backup = self._ensureBackup(self._model.dest.name(), slug)
        backup_dest = backup.getSource(self._model.dest.name())
        backup_source = backup.getSource(self._model.source.name())
        if backup_source:
            raise LogicError("This backup already exists in Home Assistant")
        if not backup_dest:
            # Unreachable?
            raise LogicError("This backup isn't in Google Drive")
        created = await self._model.source.save(backup, await self._model.dest.read(backup))
        backup.addSource(created)
        self._updateFreshness()

    async def startBackup(self, options: CreateOptions):
        return await self._withSoftLock(lambda: self._startBackup(options))

    async def _startBackup(self, options: CreateOptions):
        self.clearCaches()
        model = self._buildModel()
        self._estimator.refresh()
        if model.source.needsSpaceCheck:
            self._estimator.checkSpace(self.backups())
        created = await self._buildModel().source.create(options)
        backup = Backup(created)
        self._model.backups[backup.slug()] = backup
        self._updateFreshness()
        self._estimator.refresh()
        return backup

    def getBackup(self, slug):
        return self._ensureBackup(None, slug)

    async def download(self, slug):
        self.clearCaches()
        backup = self._ensureBackup(None, slug)
        for source in self._sources.values():
            if not source.enabled():
                continue
            if backup.getSource(source.name()):
                return await source.read(backup)
        raise NoBackup()

    async def retain(self, sources: Dict[str, bool], slug: str):
        self.clearCaches()
        for source in sources:
            backup = self._ensureBackup(source, slug)
            await self._ensureSource(source).retain(backup, sources[source])
        self._updateFreshness()

    async def note(self, note: str, slug: str):
        self.clearCaches()
        backup = self._ensureBackup(None, slug)
        for source in backup.sources.keys():
            await self._ensureSource(source).note(backup, note)

    async def delete(self, sources, slug):
        await self._withSoftLock(lambda: self._delete(sources, slug))

    async def ignore(self, slug: str, ignore: bool):
        await self._withSoftLock(lambda: self._ignore(slug, ignore))

    async def _delete(self, sources, slug):
        self.clearCaches()
        for source in sources:
            backup = self._ensureBackup(source, slug)
            await self._ensureSource(source).delete(backup)
            if backup.isDeleted():
                del self._model.backups[slug]
        self._updateFreshness()

    async def _ignore(self, slug: str, ignore: bool):
        self.clearCaches()
        backup = self._ensureBackup(SOURCE_HA, slug)
        await self._ensureSource(SOURCE_HA).ignore(backup, ignore)

    def _ensureBackup(self, source: str = None, slug=None) -> Backup:
        backup = self._buildModel().backups.get(slug)
        if not backup:
            raise NoBackup()
        if not source:
            return backup
        if not source:
            return backup
        if not backup.getSource(source):
            raise NoBackup()
        return backup

    def _ensureSource(self, source):
        ret = self._sources.get(source)
        if ret and ret.enabled():
            return ret
        raise LogicError()

    def _buildModel(self) -> Model:
        self._model.reinitialize(self._precache)
        return self._model

    def _updateFreshness(self):
        purges = self._buildModel().getNextPurges()
        for backup in self._model.backups.values():
            for source in purges:
                if backup.getSource(source):
                    backup.updatePurge(source, backup == purges[source])

    def clearCaches(self):
        if self._precache:
            self._precache.clear()

    async def _withSoftLock(self, callable):
        with self._lock:
            if self._busy:
                raise PleaseWait()
            self._busy = True
        try:
            return await callable()
        finally:
            with self._lock:
                self._busy = False
