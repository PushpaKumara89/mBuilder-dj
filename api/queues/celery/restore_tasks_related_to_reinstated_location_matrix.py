from mbuild.settings import app as celery_app

from api.queues.core.restore_tasks_related_to_reinstated_location_matrix import \
    restore_tasks_related_to_reinstated_location_matrix as restore_tasks_related_to_reinstated_location_matrix_core


@celery_app.task(queue='default', time_limit=3600)
def restore_tasks_related_to_reinstated_location_matrix(location_matrices, user):
    restore_tasks_related_to_reinstated_location_matrix_core(location_matrices, user)
