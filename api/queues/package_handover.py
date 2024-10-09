from api.queues.core.base import use_rq_if_configured

from api.queues.celery.package_handover import \
    cascade_delete_package_handover as cascade_delete_package_handover_celery, \
    create_or_restore_package_handover as create_or_restore_package_handover_celery
from api.queues.rq.package_handover import cascade_delete_package_handover as cascade_delete_package_handover_rq, \
    create_or_restore_package_handover as create_or_restore_package_handover_rq


@use_rq_if_configured(cascade_delete_package_handover_rq)
def cascade_delete_package_handover(package_matrices_ids: list):
    cascade_delete_package_handover_celery.delay(package_matrices_ids)


@use_rq_if_configured(create_or_restore_package_handover_rq)
def create_or_restore_package_handover(package_matrices: list):
    create_or_restore_package_handover_celery.delay(package_matrices)
