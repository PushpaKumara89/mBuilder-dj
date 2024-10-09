from api.services.task_entity_service import TaskEntityService


def restore_related_to_hidden_qct_tasks(activity_task_pk, project_pk, package_matrix, user):
    TaskEntityService().restore_for_shown_package_activity_task(activity_task_pk, project_pk, package_matrix, user)
