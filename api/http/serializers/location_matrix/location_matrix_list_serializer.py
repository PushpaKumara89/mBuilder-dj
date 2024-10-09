from django.db import connection
from safedelete import SOFT_DELETE

from api.http.serializers.dependent_entity_list_sync_serializer import DependentEntityListSyncSerializer
from api.models import PackageMatrix, LocationMatrixPackage
from api.queues.asset_handover import cascade_delete_asset_handover, restore_asset_handover
from api.queues.floor_plan import update_floor_plan_with_areas
from api.queues.hard_delete_tasks import hard_delete_tasks
from api.queues.package_handover import cascade_delete_package_handover, create_or_restore_package_handover
from api.queues.restore_tasks_related_to_reinstated_location_matrix import restore_tasks_related_to_reinstated_location_matrix
from api.queues.subtask_update import delete_on_location_matrix_delete
from api.queues.task import delete_tasks, restore_tasks
from api.utilities.helpers import Request


class LocationMatrixListSerializer(DependentEntityListSyncSerializer):
    _fields_to_update = ['building', 'level', 'area']
    _ignore_on_update = ['project', 'delete_matrix']
    _parent_relation_field = 'project_id'

    # Remove deleted entities from initial data
    # to avoid validation error for non-existing entity
    def _delete_nonexistent(self) -> None:
        data = self.initial_data if hasattr(self, 'initial_data') else []
        existing_ids = []

        for i, entity in enumerate(data):
            if 'id' in entity and entity.get('delete_matrix'):
                existing_ids.append(entity['id'])

        self.initial_data = [entity for entity in data if not entity.get('delete_matrix')]

        self.child.Meta.model.objects.filter(pk__in=existing_ids).delete(force_policy=SOFT_DELETE)

        delete_tasks({'location_matrix_id__in': existing_ids})

        deleted_location_matrices = self.child.Meta.model.deleted_objects.filter(pk__in=existing_ids).all()

        if deleted_location_matrices:
            lmps = LocationMatrixPackage.all_objects.filter(location_matrix__in=list(deleted_location_matrices)).all()
            package_activities = set(map(lambda lmp: lmp.package_activity_id, lmps))
            project = next(iter(deleted_location_matrices)).project
            pa_without_ticked_locations = []

            for package_activity in package_activities:
                def does_enabled_lmp_exist():
                    return LocationMatrixPackage.objects.filter(package_matrix__project=project,
                                                                location_matrix__deleted__isnull=True,
                                                                package_activity_id=package_activity,
                                                                enabled=True).exists()
                if not does_enabled_lmp_exist():
                    pa_without_ticked_locations.append(package_activity)

            pm = PackageMatrix.objects.filter(package_activity_id__in=pa_without_ticked_locations, project=project).all()

            cascade_delete_package_handover(list(pm))
            cascade_delete_asset_handover(list(lmps.values_list('id', flat=True)))
            context = {
                'request': Request(self.child.context['request'].user, self.child.context['request'].query_params),
                'project_pk': project.pk
            }
            delete_on_location_matrix_delete(
                [location.id for location in deleted_location_matrices],
                context
            )

        if len(existing_ids) > 0:
            hard_delete_tasks({'location_matrix_id__in': existing_ids})

    def _create_entities(self) -> None:
        new_entities = []
        restored_location_matrices = []

        for entity_data in self._new_entities_data:
            location_matrix_data = {key: value for key, value in entity_data.items() if key != 'project'}
            if self.child.Meta.model.deleted_objects.filter(**location_matrix_data).exists():
                self.child.Meta.model.deleted_objects.filter(**entity_data).undelete()
                restored_location_matrices += list(self.child.Meta.model.objects.filter(**entity_data).all())
            else:
                new_entities.append(self.child.Meta.model(**entity_data))

        restore_tasks({
            'location_matrix_id__in': [location_matrix.id for location_matrix in restored_location_matrices]
        })

        if restored_location_matrices:
            lmps = LocationMatrixPackage.objects.filter(location_matrix__in=restored_location_matrices).all()
            package_activities = set(map(lambda lmp: lmp.package_activity_id, lmps))
            project = next(iter(restored_location_matrices)).project
            pa_with_ticked_locations = []

            for package_activity in package_activities:
                def does_enabled_lmp_exist():
                    return LocationMatrixPackage.objects.filter(package_matrix__project=project,
                                                                package_activity_id=package_activity,
                                                                location_matrix__deleted__isnull=True,
                                                                enabled=True).exists()
                if does_enabled_lmp_exist():
                    pa_with_ticked_locations.append(package_activity)

            pm = PackageMatrix.objects.filter(package_activity_id__in=pa_with_ticked_locations, project=project).all()

            create_or_restore_package_handover(list(pm))
            restore_asset_handover(list(lmps.values_list('id', flat=True)))

            restore_tasks_related_to_reinstated_location_matrix(
                restored_location_matrices, self.child.context['request'].user
            )

        created_entities = self.child.Meta.model.objects.bulk_create(new_entities)

        if created_entities:
            self.__create_location_matrix_packages(created_entities)

    def __create_location_matrix_packages(self, location_matrices) -> None:
        location_matrix_packages = list()
        project_package_matrix = PackageMatrix.objects.filter(project=location_matrices[0].project).select_related(
            'package',
            'package_activity'
        ).all()

        for location_matrix in location_matrices:
            for package_matrix in project_package_matrix:
                location_matrix_package = LocationMatrixPackage(
                    location_matrix=location_matrix,
                    package_matrix=package_matrix,
                    package=package_matrix.package,
                    package_activity=package_matrix.package_activity,
                    package_activity_name=package_matrix.package_activity.name
                )
                location_matrix_packages.append(location_matrix_package)

        LocationMatrixPackage.objects.bulk_create(location_matrix_packages, batch_size=500)

    def _update_entities(self) -> None:
        entities_ids = {item['id'] for item in self._existing_entities_data}
        location_matrices = self.child.Meta.model.objects.filter(id__in=entities_ids).all()
        update_floor_plan_with_areas(location_matrices, self._existing_entities_data)

        super()._update_entities()

        if entities_ids:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE tasks SET building = location_matrix.building,
                                     level = location_matrix.level,
                                     area = location_matrix.area
                    FROM location_matrix
                    WHERE location_matrix.id = location_matrix_id
                      AND location_matrix_id IN %s
                """, (tuple(entities_ids),))
