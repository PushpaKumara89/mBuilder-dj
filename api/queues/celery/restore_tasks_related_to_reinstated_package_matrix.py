from mbuild.settings import app as celery_app

from api.queues.core.restore_tasks_related_to_reinstated_package_matrix import \
    restore_tasks_related_to_reinstated_package_matrix as restore_tasks_related_to_reinstated_package_matrix_core


@celery_app.task(queue='default', time_limit=3600)
def restore_tasks_related_to_reinstated_package_matrix(package_activity, location_matrix_packages: list, location_matrix, user):
    restore_tasks_related_to_reinstated_package_matrix_core(package_activity, location_matrix_packages, location_matrix, user)
