from django_rq import job

from api.queues.core.edit_mode import remove_user_project_edit_mode as remove_user_project_edit_mode_core


@job('edit_mode', timeout=60)
def remove_user_project_edit_mode(user: int, project: int):
    remove_user_project_edit_mode_core(user, project)
