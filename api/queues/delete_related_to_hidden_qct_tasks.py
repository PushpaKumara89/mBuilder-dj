from api.queues.core.base import use_rq_if_configured
from api.queues.rq.delete_related_to_hidden_qct_tasks import \
    delete_related_to_hidden_qct_tasks as delete_related_to_hidden_qct_tasks_rq
from api.queues.celery.delete_related_to_hidden_qct_tasks import \
    delete_related_to_hidden_qct_tasks as delete_related_to_hidden_qct_tasks_celery


@use_rq_if_configured(delete_related_to_hidden_qct_tasks_rq)
def delete_related_to_hidden_qct_tasks(filters: dict) -> None:
    delete_related_to_hidden_qct_tasks_celery.delay(filters)
