import pendulum
from django.conf import settings
from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class WeeklySummaryJob(CronJobBase):
    schedule = Schedule(run_at_times=[settings.SUMMARY_RUN_AT_TIME])
    code = 'api.jobs.WeeklySummaryJob'

    @sentry_exceptions
    def do(self):
        if pendulum.now().weekday() == pendulum.SUNDAY:
            management.call_command('send_summaries', 'weekly')
