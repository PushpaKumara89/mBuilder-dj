from django.db.models import Q

from api.models import AssetHandover, LocationMatrixPackage


def cascade_delete_asset_handover(location_matrix_packages: list[int]) -> None:
    location_matrix_packages = LocationMatrixPackage.all_objects.filter(id__in=location_matrix_packages).all()
    filters = None
    for lmp in location_matrix_packages:
        condition = Q(package_activity_id=lmp.package_activity_id, location_matrix_id=lmp.location_matrix_id)
        filters = filters | condition if filters else condition

    if filters:
        AssetHandover.objects.filter(filters).delete()


def restore_asset_handover(location_matrix_packages: list[int]) -> None:
    location_matrix_packages = LocationMatrixPackage.all_objects.filter(id__in=location_matrix_packages).all()
    filters = None
    for lmp in location_matrix_packages:
        condition = Q(package_activity_id=lmp.package_activity_id, location_matrix_id=lmp.location_matrix_id)
        filters = filters | condition if filters else condition

    if filters:
        AssetHandover.deleted_objects.filter(filters).undelete()
