from django_rq import job

from api.queues.core.delete_related_to_hidden_qct_tasks import \
    delete_related_to_hidden_qct_tasks as delete_related_to_hidden_qct_tasks_core


@job('default', timeout=3600)
def delete_related_to_hidden_qct_tasks(filters: dict):
    delete_related_to_hidden_qct_tasks_core(filters)
