from api.queues.core.base import use_rq_if_configured
from api.queues.celery.asset_handover import cascade_delete_asset_handover as cascade_delete_asset_handover_celery, \
    restore_asset_handover as restore_asset_handover_celery
from api.queues.rq.asset_handover import cascade_delete_asset_handover as cascade_delete_asset_handover_rq, \
    restore_asset_handover as restore_asset_handover_rq


@use_rq_if_configured(cascade_delete_asset_handover_rq)
def cascade_delete_asset_handover(location_matrix_packages: list[int]) -> None:
    cascade_delete_asset_handover_celery.delay(location_matrix_packages)


@use_rq_if_configured(restore_asset_handover_rq)
def restore_asset_handover(location_matrix_packages: list[int]) -> None:
    restore_asset_handover_celery.delay(location_matrix_packages)
