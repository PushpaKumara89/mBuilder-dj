from mbuild.settings import app as celery_app

from api.queues.core.destroy_project import \
    cascade_delete_project_with_related_entities as cascade_delete_project_with_related_entities_core


@celery_app.task(queue='default', time_limit=3600)
def cascade_delete_project_with_related_entities(project_pk: int) -> None:
    cascade_delete_project_with_related_entities_core(project_pk)
