from django_rq import job

from api.queues.core.restore_tasks_related_to_reinstated_package_matrix import \
    restore_tasks_related_to_reinstated_package_matrix as restore_tasks_related_to_reinstated_package_matrix_core


@job('default', timeout=3600)
def restore_tasks_related_to_reinstated_package_matrix(package_activity, location_matrix_packages: list, location_matrix, user):
    restore_tasks_related_to_reinstated_package_matrix_core(package_activity, location_matrix_packages, location_matrix,
                                                            user)
