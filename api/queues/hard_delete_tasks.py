from api.queues.core.base import use_rq_if_configured

from api.queues.rq.hard_delete_tasks import hard_delete_tasks as hard_delete_tasks_rq
from api.queues.celery.hard_delete_tasks import hard_delete_tasks as hard_delete_tasks_celery


@use_rq_if_configured(hard_delete_tasks_rq)
def hard_delete_tasks(task_filters: dict):
    hard_delete_tasks_celery.delay(task_filters)
