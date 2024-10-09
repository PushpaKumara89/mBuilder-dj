from api.queues.core.base import use_rq_if_configured
from api.queues.rq.destroy_project import \
    cascade_delete_project_with_related_entities as cascade_delete_project_with_related_entities_rq
from api.queues.celery.destroy_project import \
    cascade_delete_project_with_related_entities as cascade_delete_project_with_related_entities_celery


@use_rq_if_configured(cascade_delete_project_with_related_entities_rq)
def cascade_delete_project_with_related_entities(project_pk: int):
    cascade_delete_project_with_related_entities_celery.delay(project_pk)
