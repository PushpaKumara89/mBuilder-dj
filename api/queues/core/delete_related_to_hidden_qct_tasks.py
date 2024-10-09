from api.services.task_entity_service import TaskEntityService


def delete_related_to_hidden_qct_tasks(filters: dict):
    TaskEntityService().delete_for_hidden_package_activity_task(filters)
