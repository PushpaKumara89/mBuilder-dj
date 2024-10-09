from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class ClearPasswordResetTokenJob(CronJobBase):
    schedule = Schedule(run_every_mins=30)
    code = 'api.jobs.ClearPasswordResetTokenJob'

    @sentry_exceptions
    def do(self):
        management.call_command('clear_expired_reset_password_tokens')
