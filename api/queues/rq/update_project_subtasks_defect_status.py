from django_rq import job

from api.queues.core.update_project_subtasks_defect_status import \
    update_project_subtasks_defect_status as update_project_subtasks_defect_status_core


@job('default', timeout=3600)
def update_project_subtasks_defect_status(project_id, project_completion_date: str):
    update_project_subtasks_defect_status_core(project_id, project_completion_date)
