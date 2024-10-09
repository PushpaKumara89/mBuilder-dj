from mbuild.settings import app as celery_app

from api.queues.core.delete_related_to_hidden_qct_tasks import \
    delete_related_to_hidden_qct_tasks as delete_related_to_hidden_qct_tasks_core


@celery_app.task(queue='default', time_limit=3600)
def delete_related_to_hidden_qct_tasks(filters: dict):
    delete_related_to_hidden_qct_tasks_core(filters)
