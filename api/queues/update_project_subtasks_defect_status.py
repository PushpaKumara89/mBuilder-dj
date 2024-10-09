from api.queues.core.base import use_rq_if_configured

from api.queues.rq.update_project_subtasks_defect_status import \
    update_project_subtasks_defect_status as update_project_subtasks_defect_status_rq
from api.queues.celery.update_project_subtasks_defect_status import \
    update_project_subtasks_defect_status as update_project_subtasks_defect_status_celery


@use_rq_if_configured(update_project_subtasks_defect_status_rq)
def update_project_subtasks_defect_status(project_id, project_completion_date: str):
    update_project_subtasks_defect_status_celery.delay(project_id, project_completion_date)
