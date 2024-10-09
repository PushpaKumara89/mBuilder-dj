from django_rq import job

from api.queues.core.asset_handover import cascade_delete_asset_handover as cascade_delete_asset_handover_core, \
    restore_asset_handover as restore_asset_handover_core


@job('default', timeout=3600)
def cascade_delete_asset_handover(location_matrix_packages: list[int]) -> None:
    cascade_delete_asset_handover_core(location_matrix_packages)


@job('default', timeout=3600)
def restore_asset_handover(location_matrix_packages: list[int]) -> None:
    restore_asset_handover_core(location_matrix_packages)
