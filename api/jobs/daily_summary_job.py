from django.conf import settings
from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class DailySummaryJob(CronJobBase):
    schedule = Schedule(run_at_times=[settings.SUMMARY_RUN_AT_TIME])
    code = 'api.jobs.DailySummaryJob'

    @sentry_exceptions
    def do(self):
        management.call_command('send_summaries', 'daily')
