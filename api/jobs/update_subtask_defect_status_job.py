from django.conf import settings
from django.core import management
from django_cron import CronJobBase, Schedule

from api.jobs.helpers import sentry_exceptions


class UpdateSubtaskDefectStatusJob(CronJobBase):
    schedule = Schedule(run_every_mins=settings.SUBTASK_DEFECT_STATUS_UPDATE_IN_MINUTES)
    code = 'api.jobs.UpdateSubtaskDefectStatusJob'

    @sentry_exceptions
    def do(self):
        management.call_command('update_subtask_defect_status')
