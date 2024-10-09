from django.conf import settings
from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class RecalculateStatisticsJob(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = 'api.jobs.RecalculateStatisticsJob'

    @sentry_exceptions
    def do(self):
        management.call_command('fill_handover_statistics_by_group_company', '--clear-package-handover')
        management.call_command('fill_handover_statistics_by_group_company', '--only-package-handover')
        management.call_command('fill_summarized_handover_statistics', '--clear-package-handover')
        management.call_command('fill_summarized_handover_statistics', '--only-package-handover')

        management.call_command('fill_handover_statistics_by_group_company', '--clear-asset-handover')
        management.call_command('fill_handover_statistics_by_group_company', '--only-asset-handover')
        management.call_command('fill_summarized_handover_statistics', '--clear-asset-handover')
        management.call_command('fill_summarized_handover_statistics', '--only-asset-handover')

