from mbuild.settings import app as celery_app

from api.queues.core.hard_delete_tasks import hard_delete_tasks as hard_delete_tasks_core


@celery_app.task(queue='default', time_limit=3600)
def hard_delete_tasks(task_filters: dict):
    hard_delete_tasks_core(task_filters)
