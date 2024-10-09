from mbuild.settings import app as celery_app

from api.queues.core.package_handover import create_package_handover, restore_package_handover, \
    get_package_handover_by_package_matrix, cascade_delete_package_handover as cascade_delete_package_handover_core

from api.queues.celery.handover_document import undelete_handover_document_on_package_handover_undelete
from api.queues.celery.package_handover_statistics import undelete_statistics_on_package_handover_undelete


@celery_app.task(queue='default', time_limit=3600)
def cascade_delete_package_handover(package_matrices_ids: list):
    cascade_delete_package_handover_core(package_matrices_ids)


@celery_app.task(queue='default', time_limit=3600)
def create_or_restore_package_handover(package_matrices: list):
    for package_matrix in package_matrices:
        package_handover = get_package_handover_by_package_matrix(package_matrix)

        if package_handover and package_handover.deleted:
            package_handover = restore_package_handover(package_handover, package_matrix)

            undelete_statistics_on_package_handover_undelete.delay(package_handover)
            undelete_handover_document_on_package_handover_undelete.delay(package_handover)
        elif not package_handover:
            create_package_handover(package_matrix)
