﻿using Newtonsoft.Json;
using System.Text.Json.Serialization;
using JsonIgnoreAttribute = Newtonsoft.Json.JsonIgnoreAttribute;

namespace hassio_onedrive_backup.Contracts
{
    public class AddonOptions
    {
        [JsonProperty("local_backup_num_to_keep")]
        public int MaxLocalBackups { get; set; }

        [JsonProperty("onedrive_backup_num_to_keep")]
        public int MaxOnedriveBackups { get; set; }

        [JsonProperty("backup_interval_days")]
        public float BackupIntervalDays { get; set; }

        [JsonProperty("backup_passwd")]
        public string? BackupPassword { get; set; }

        [JsonProperty("backup_name")]
        public string? BackupName { get; set; }

        [JsonProperty("monitor_all_local_backups")]
        public bool MonitorAllLocalBackups{ get; set; }

        [JsonProperty("notify_on_error")]
        public bool NotifyOnError { get; set; }

        [JsonProperty("hass_api_timeout_minutes")]
        public int HassAPITimeoutMinutes { get; set; }

        [JsonProperty("exclude_media_folder")]
        public bool ExcludeMediaFolder { get; set; }

        [JsonProperty("exclude_ssl_folder")]
        public bool ExcludeSSLFolder { get; set; }

        [JsonProperty("exclude_share_folder")]
        public bool ExcludeShareFolder { get; set; }

        [JsonProperty("exclude_local_addons_folder")]
        public bool ExcludeLocalAddonsFolder { get; set; }

        [JsonProperty("backup_allowed_hours")]
        public string? BackupAllowedHours { get; set; }

        [JsonProperty("backup_instance_name")]
        public string? InstanceName { get; set; }

        [JsonProperty("sync_paths")]
        public List<string>? SyncPaths { get; set; }

        [JsonProperty("file_sync_remove_deleted")]
        public bool FileSyncRemoveDeleted { get; set; } = false;

        [JsonProperty("excluded_addons")]
        public List<string> ExcludedAddons { get; set; } = new List<string>();

		[JsonProperty("log_level")]
		public string LogLevelStr { get; set; }

        [JsonProperty("ignore_upgrade_backups")]
        public bool IgnoreUpgradeBackups { get; set; }

        //[JsonProperty("upload_speed_cap")]
        //public int? UploadSpeedCapKBPerSecond { get; set; }

        [JsonIgnore]
		public ConsoleLogger.LogLevel LogLevel => LogLevelStr switch
        {
			"verbose" => ConsoleLogger.LogLevel.Verbose,
			"info" => ConsoleLogger.LogLevel.Info,
			"warning" => ConsoleLogger.LogLevel.Warning,
			"error" => ConsoleLogger.LogLevel.Error,
			_ => ConsoleLogger.LogLevel.Info
		};

        [JsonIgnore]
		public string BackupPasswordSafe => string.IsNullOrEmpty(BackupPassword) ? "backup" : BackupPassword;
		[JsonIgnore]
        public float BackupIntervalHours => BackupIntervalDays * 24;

        [JsonIgnore]
        public string BackupNameSafe => string.IsNullOrEmpty(BackupName) ? "hass_backup" : BackupName;

        [JsonIgnore]
        public bool IsPartialBackup => ExcludeLocalAddonsFolder || ExcludeMediaFolder || ExcludeShareFolder || ExcludeSSLFolder || ExcludedAddons.Any();

        [JsonIgnore]
        public bool FileSyncEnabled => SyncPaths != null && SyncPaths.Count > 0;

        //[JsonIgnore]
        //public bool UploadSpeedCap => UploadSpeedCapKBPerSecond != null;
        
        public List<string> IncludedFolderList
        {
            get
            {
                List<string> folders = new List<string>();
                if (!ExcludeLocalAddonsFolder)
                {
                    folders.Add("addons/local");
                }

                if (!ExcludeMediaFolder)
                {
                    folders.Add("media");
                }

                if (!ExcludeShareFolder)
                {
                    folders.Add("share");
                }

                if (!ExcludeSSLFolder)
                {
                    folders.Add("ssl");
                }

                return folders;
            }
        }
    }
}
