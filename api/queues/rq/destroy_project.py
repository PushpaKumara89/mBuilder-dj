from django_rq import job

from api.queues.core.destroy_project import \
    cascade_delete_project_with_related_entities as cascade_delete_project_with_related_entities_core


@job('default', timeout=3600)
def cascade_delete_project_with_related_entities(project_pk: int):
    cascade_delete_project_with_related_entities_core(project_pk)
