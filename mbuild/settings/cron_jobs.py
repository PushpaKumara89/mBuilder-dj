from mbuild.settings.common import ENV


CRON_CLASSES = [
    'api.jobs.ClearPasswordResetTokenJob',
    'api.jobs.UpdateSubtaskDefectStatusJob',
    'api.jobs.RemoveExpiredEditModeJob',
    'api.jobs.RecalculateStatisticsJob',
]

if ENV != 'staging':
    CRON_CLASSES.append('api.jobs.DailySummaryJob')
    CRON_CLASSES.append('api.jobs.WeeklySummaryJob')

