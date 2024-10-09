from rest_framework.serializers import ListSerializer

from api.dataclasses.location_matrix_package import LocationMatrixPackageSyncParams
from api.models import LocationMatrixPackage, PackageMatrix
from api.queues.hard_delete_tasks import hard_delete_tasks
from api.queues.asset_handover import cascade_delete_asset_handover
from api.queues.core.location_matrix_package import is_package_activity_picked_in_project
from api.queues.package_handover import create_or_restore_package_handover, cascade_delete_package_handover
from api.queues.task import restore_related_tasks_with_entities


class LocationMatrixPackageListSerializer(ListSerializer):
    updated_entities = []
    _fields_to_update = ['enabled']
    _is_validation_required = False

    _exclude_field_list = [
        'id', 'package', 'package_activity', 'package_activity_name'
    ]

    def sync(self, user) -> None:
        if hasattr(self, 'initial_data') and len(self.initial_data) > 0:
            self._validate()
            self._existing_entities_data = self.validated_data
            self._update_entities(user)

    def _validate(self) -> None:
        if self._is_validation_required:
            self.is_valid(raise_exception=True)
        else:
            self._validated_data = self.initial_data

    def _update_entities(self, user):
        def get_project():
            lmp = next(iter(location_matrix_packages))
            return lmp.package_matrix.project if lmp else None

        entities_ids = [existing_entity['id'] for existing_entity in self._existing_entities_data]
        location_matrix_packages = self.child.Meta.model.objects \
            .filter(pk__in=entities_ids) \
            .select_related('package_matrix__package_activity') \
            .all()
        sync_data: list[LocationMatrixPackageSyncParams] = []
        enabling_lmp_activities = []
        enabling_lmps = []
        disabling_lmps = []
        project = get_project()

        for location_matrix_package in location_matrix_packages:
            updated_location_matrix_package = next(item for item in self._existing_entities_data if item['id'] == location_matrix_package.pk)
            for field_to_update in self._fields_to_update:
                def is_location_matrix_package_enabled():
                    return field_to_update == 'enabled' and \
                           location_matrix_package.enabled != updated_location_matrix_package['enabled'] and \
                           updated_location_matrix_package['enabled']

                def is_location_matrix_package_disabled():
                    return field_to_update == 'enabled' and \
                           location_matrix_package.enabled != updated_location_matrix_package['enabled'] and \
                           not updated_location_matrix_package['enabled']

                if is_location_matrix_package_enabled():
                    enabling_lmps.append(location_matrix_package)
                    enabling_lmp_activities.append(location_matrix_package.package_activity_id)

                if is_location_matrix_package_disabled():
                    disabling_lmps.append(location_matrix_package)

                setattr(location_matrix_package, field_to_update, updated_location_matrix_package[field_to_update])

            sync_data.append(
                LocationMatrixPackageSyncParams(
                    location_matrix_package=location_matrix_package,
                    updated_location_matrix_package=updated_location_matrix_package,
                    user=user
                )
            )

        # Firstly, detect package activities that enabled in current request.
        # We need to apply package handover create or restore only for them,
        # not for all enabled package activities in project.
        # It helps us to optimize script resources, because package activities may be hundreds
        # with thousands related enabled locations.
        enabled_in_request_activities = []
        if project:
            activities_with_enabled_lmp = LocationMatrixPackage.objects.filter(
                package_activity__in=set(enabling_lmp_activities),
                package_matrix__project=project,
                package_matrix__deleted__isnull=True,
                package_matrix__packagehandover__isnull=False,
                enabled=True
            ).values_list('package_activity_id', flat=True)

            enabled_in_request_activities = set(enabling_lmp_activities) - set(activities_with_enabled_lmp)

        self.child.Meta.model.objects.bulk_update(location_matrix_packages, self._fields_to_update, batch_size=500)

        if disabling_lmps:
            cascade_delete_asset_handover([disabling_lmp.id for disabling_lmp in disabling_lmps])

        if enabled_in_request_activities:
            package_matrices = PackageMatrix.objects.filter(package_activity_id__in=enabled_in_request_activities,
                                                            project=project).all()
            create_or_restore_package_handover(list(package_matrices))

        self.updated_entities = self.child.Meta.model.objects.filter(pk__in=entities_ids)

        self._sync_entities(sync_data)

    def _sync_entities(self, sync_data: list[LocationMatrixPackageSyncParams]) -> None:
        for sync_params in sync_data:
            if sync_params.updated_location_matrix_package['enabled']:
                restore_related_tasks_with_entities(sync_params.location_matrix_package, sync_params.user)
            else:
                hard_delete_tasks({
                    'location_matrix': sync_params.location_matrix_package.location_matrix_id,
                    'package_activity': sync_params.location_matrix_package.package_activity_id
                })

                if not is_package_activity_picked_in_project(sync_params.location_matrix_package):
                    cascade_delete_package_handover([sync_params.location_matrix_package.package_matrix.pk])
