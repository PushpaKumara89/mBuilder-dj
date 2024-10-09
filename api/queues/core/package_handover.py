from api.models import LocationMatrixPackage, PackageMatrix, PackageHandover


def cascade_delete_package_handover(package_matrices_ids: list):
    from api.models import PackageHandover

    PackageHandover.objects.filter(package_matrix__in=package_matrices_ids).delete()


def create_package_handover(package_matrix: PackageMatrix) -> None:
    # Package matrices that created before adding package handover functionality don't have
    # related deleted package handover. Create the last one.
    from api.http.serializers import PackageHandoverSerializer

    if does_package_activity_has_ticked_locations_in_project(package_matrix):
        serializers = PackageHandoverSerializer(data={'package_matrix': package_matrix.pk})
        serializers.is_valid(raise_exception=True)
        serializers.create(serializers.validated_data)


def restore_package_handover(package_handover: PackageHandover, package_matrix: PackageMatrix) -> PackageHandover:
    setattr(package_handover, 'deleted', None)
    setattr(package_handover, 'package_matrix', package_matrix)
    package_handover.save(update_fields=['deleted', 'package_matrix'])

    return package_handover


def get_package_handover_by_package_matrix(package_matrix: PackageMatrix) -> PackageHandover:
    # Package handover displays grouped by project package activity.
    # Even if we move package activity from one package to another,
    # we should save package handover documents.
    # In this case package activity stay in the project, but
    # related to different package matrix. Update to this package matrix.
    return PackageHandover.all_objects.filter(
        package_matrix__package_activity=package_matrix.package_activity,
        package_matrix__project=package_matrix.project).first()


def does_package_activity_has_ticked_locations_in_project(package_matrix: PackageMatrix) -> bool:
    return LocationMatrixPackage.objects.filter(package_activity=package_matrix.package_activity, enabled=True,
                                                package_matrix__project=package_matrix.project).exists()
