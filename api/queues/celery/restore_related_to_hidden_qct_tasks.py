from mbuild.settings import app as celery_app

from api.queues.core.restore_related_to_hidden_qct_tasks import restore_related_to_hidden_qct_tasks as restore_related_to_hidden_qct_tasks_core


@celery_app.task(queue='default', time_limit=3600)
def restore_related_to_hidden_qct_tasks(activity_task_pk, project_pk, package_matrix, user):
    restore_related_to_hidden_qct_tasks_core(activity_task_pk, project_pk, package_matrix, user)
