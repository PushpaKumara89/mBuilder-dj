from django_rq import job

from api.queues.core.restore_tasks_related_to_reinstated_location_matrix import \
    restore_tasks_related_to_reinstated_location_matrix as restore_tasks_related_to_reinstated_location_matrix_core


@job('default', timeout=3600)
def restore_tasks_related_to_reinstated_location_matrix(location_matrices, user):
    restore_tasks_related_to_reinstated_location_matrix_core(location_matrices, user)
