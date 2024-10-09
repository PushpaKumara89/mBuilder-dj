from api.queues.core.location_matrix_package import restore_related_tasks_with_entities as restore_related_tasks_with_entities_core
from mbuild.settings import app as celery_app

from api.queues.core.task import delete_tasks as delete_tasks_core
from api.queues.core.task import restore_tasks as restore_tasks_core


@celery_app.task(queue='tasks', time_limit=3600)
def delete_tasks(filters: dict) -> None:
    delete_tasks_core(filters)


@celery_app.task(queue='tasks', time_limit=3600)
def restore_tasks(filters: dict) -> None:
    restore_tasks_core(filters)


@celery_app.task(queue='tasks', time_limit=3600)
def restore_related_tasks_with_entities(location_matrix_package, user) -> None:
    restore_related_tasks_with_entities_core(location_matrix_package, user)
