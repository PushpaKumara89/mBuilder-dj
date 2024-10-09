from api.queues.core.base import use_rq_if_configured
from api.queues.rq.task import delete_tasks as delete_task_rq, restore_related_tasks_with_entities as restore_related_tasks_with_entities_rq
from api.queues.rq.task import restore_tasks as restore_task_rq
from api.queues.celery.task import delete_tasks as delete_task_celery, restore_related_tasks_with_entities as restore_related_tasks_with_entities_celery
from api.queues.celery.task import restore_tasks as restore_task_celery


@use_rq_if_configured(delete_task_rq)
def delete_tasks(task_filters: dict):
    delete_task_celery.delay(task_filters)


@use_rq_if_configured(restore_task_rq)
def restore_tasks(task_filters: dict):
    restore_task_celery.delay(task_filters)


@use_rq_if_configured(restore_related_tasks_with_entities_rq)
def restore_related_tasks_with_entities(location_matrix_package, user):
    restore_related_tasks_with_entities_celery.delay(location_matrix_package, user)
