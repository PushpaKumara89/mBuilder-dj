from django_rq import job

from api.queues.core.hard_delete_tasks import hard_delete_tasks as hard_delete_tasks_core


@job('default', timeout=3600)
def hard_delete_tasks(task_filters: dict):
    hard_delete_tasks_core(task_filters)
