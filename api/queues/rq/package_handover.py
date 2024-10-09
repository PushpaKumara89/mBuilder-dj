from django_rq import job

from api.queues.core.package_handover import create_package_handover, restore_package_handover, \
    get_package_handover_by_package_matrix, cascade_delete_package_handover as cascade_delete_package_handover_core

from api.queues.rq.handover_document import undelete_handover_document_on_package_handover_undelete
from api.queues.rq.package_handover_statistics import undelete_statistics_on_package_handover_undelete


@job('default', timeout=3600)
def cascade_delete_package_handover(package_matrices_ids: list):
    cascade_delete_package_handover_core(package_matrices_ids)


@job('default', timeout=3600)
def create_or_restore_package_handover(package_matrices: list):
    for package_matrix in package_matrices:
        package_handover = get_package_handover_by_package_matrix(package_matrix)

        if package_handover and package_handover.deleted:
            package_handover = restore_package_handover(package_handover, package_matrix)

            undelete_statistics_on_package_handover_undelete.delay(package_handover)
            undelete_handover_document_on_package_handover_undelete.delay(package_handover)
        elif not package_handover:
            create_package_handover(package_matrix)
