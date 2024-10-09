from api.queues.core.base import use_rq_if_configured

from api.queues.rq.restore_tasks_related_to_reinstated_package_matrix import \
    restore_tasks_related_to_reinstated_package_matrix as restore_tasks_related_to_reinstated_package_matrix_rq
from api.queues.celery.restore_tasks_related_to_reinstated_package_matrix import \
    restore_tasks_related_to_reinstated_package_matrix as restore_tasks_related_to_reinstated_package_matrix_celery


@use_rq_if_configured(restore_tasks_related_to_reinstated_package_matrix_rq)
def restore_tasks_related_to_reinstated_package_matrix(package_activity, location_matrix_packages: list, location_matrix, user):
    restore_tasks_related_to_reinstated_package_matrix_celery.delay(package_activity, location_matrix_packages, location_matrix, user)
