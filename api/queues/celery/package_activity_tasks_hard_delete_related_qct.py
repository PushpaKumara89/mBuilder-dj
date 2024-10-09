from mbuild.settings import app as celery_app

from api.queues.core.package_activity_tasks_hard_delete_related_qct import \
    package_activity_tasks_hard_delete_related_qct as package_activity_tasks_hard_delete_related_qct_core


@celery_app.task(queue='default', time_limit=3600)
def package_activity_tasks_hard_delete_related_qct(task_filters: dict, task_exclude_filters: dict = None):
    package_activity_tasks_hard_delete_related_qct_core(task_filters, task_exclude_filters)
