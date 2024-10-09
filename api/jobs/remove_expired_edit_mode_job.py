from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class RemoveExpiredEditModeJob(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = 'api.jobs.RemoveExpiredEditModeJob'

    @sentry_exceptions
    def do(self):
        management.call_command('remove_expired_edit_mode')
