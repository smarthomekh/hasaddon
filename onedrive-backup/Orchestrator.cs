using hassio_onedrive_backup.Contracts;
using hassio_onedrive_backup.Graph;
using hassio_onedrive_backup.Hass;
using hassio_onedrive_backup.Sync;
using onedrive_backup.Graph;
using System.Collections;

namespace hassio_onedrive_backup
{
    public class Orchestrator
    {
        private readonly IHassioClient _hassIoClient;
        private readonly HassOnedriveFreeSpaceEntityState? _hassOnedriveFreeSpaceEntityState;
        private readonly IGraphHelper _graphHelper;
        private readonly IServiceProvider _serviceProvider;
        private readonly AddonOptions _addonOptions;
        private readonly BitArray _allowedBackupHours;

        private bool _enabled = false;

        public Orchestrator(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
            _addonOptions = serviceProvider.GetService<AddonOptions>();
            _graphHelper = serviceProvider.GetService<IGraphHelper>();
            _hassIoClient = serviceProvider.GetService<IHassioClient>();
            _hassOnedriveFreeSpaceEntityState = serviceProvider.GetService<HassOnedriveFreeSpaceEntityState>();

            _allowedBackupHours = TimeRangeHelper.GetAllowedHours(_addonOptions.BackupAllowedHours);
            BackupManager = new BackupManager(_serviceProvider, _allowedBackupHours, new TransferSpeedHelper(null));
        }

        public BackupManager BackupManager { get; set; }

        public async Task Start()
        {
            _enabled = true;
            string timeZoneId = await _hassIoClient.GetTimeZoneAsync();
            DateTimeHelper.Initialize(timeZoneId);
            TimeSpan intervalDelay = TimeSpan.FromMinutes(5);

            ConsoleLogger.LogInfo($"Backup interval configured to every {_addonOptions.BackupIntervalHours} hours");
            if (string.IsNullOrWhiteSpace(_addonOptions.BackupAllowedHours) == false)
            {
                ConsoleLogger.LogInfo($"Backups / Syncs will only run during these hours: {_allowedBackupHours.ToAllowedHoursText()}");
            }

            //if (_addonOptions.UploadSpeedCap)
            //{
            //    ConsoleLogger.LogInfo($"Upload speed configured to cap at {_addonOptions.UploadSpeedCapKBPerSecond} KB/s");
            //}

            // Initialize File Sync Manager
            if (_addonOptions.FileSyncEnabled)
            {
				ConsoleLogger.LogInfo($"File Sync Enabled");
                var transferSpeedHelper = new TransferSpeedHelper(null);
                var syncManager = new SyncManager(_serviceProvider, _allowedBackupHours, transferSpeedHelper);
                var tokenSource = new CancellationTokenSource();
                await _graphHelper.GetAndCacheUserTokenAsync();
                var fileSyncTask = Task.Run(() => syncManager.SyncLoop(tokenSource.Token), tokenSource.Token);
            }
            else
            {
                ConsoleLogger.LogInfo($"File Sync Disabled");
            }

			while (_enabled)
            {
                try
                {
                    // Refresh Graph Token
                    await _graphHelper.GetAndCacheUserTokenAsync();

                    // Update OneDrive Freespace Sensor
                    var oneDriveSpace = await _graphHelper.GetFreeSpaceInGB();
                    if (oneDriveSpace != null)
                    {
						await _hassOnedriveFreeSpaceEntityState.UpdateOneDriveFreespaceSensorInHass(oneDriveSpace);
					}

					ConsoleLogger.LogVerbose("Checking backups");

                    BackupManager.PerformBackupsAsync();
                }
                catch (Exception ex)
                {
                    ConsoleLogger.LogError($"Unexpected error. {ex}");
                }

                ConsoleLogger.LogVerbose("Backup Interval Completed.");
                await Task.Delay(intervalDelay);
            }
        }

        public void Stop()
        {
            _enabled = false;
        }
    }
}
