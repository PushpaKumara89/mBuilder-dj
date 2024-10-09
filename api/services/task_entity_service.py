import pendulum
from django.db.models import Exists, OuterRef
from typing import Dict, Type

from api.models import Task, PackageActivityTask, LocationMatrixPackage, Package
from api.models.base_model import BaseModel
from api.services.base_entity_service import BaseEntityService
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.services.subtask_entity_service import SubtaskEntityService
from api.utilities.tasks_utilities import get_task_status, create_task_updates


class TaskEntityService(BaseEntityService):
    model = Task

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        location_matrix = validated_data['location_matrix']
        validated_data['building'] = location_matrix.building
        validated_data['level'] = location_matrix.level
        validated_data['area'] = location_matrix.area
        validated_data['package'] = Package.objects.filter(
            packagematrix__project=kwargs['project_pk'],
            packagematrix__package_activity=validated_data['package_activity']
        ).first()

        return super().create(validated_data, **kwargs)

    def update(self, instance: Task, validated_data: dict, **kwargs) -> Task:
        self._set_date_of_approval(instance, validated_data)

        return super().update(instance, validated_data)

    def delete_for_hidden_package_activity_task(self, filters: dict) -> None:
        tasks = Task.objects.filter(**filters).all()

        SubtaskEntityService().delete_for_hidden_package_activity_task(tasks)
        QualityIssueEntityService().delete_for_hidden_package_activity_task(tasks)

        tasks.delete()

    def restore_for_shown_package_activity_task(self, activity_task_pk: int, project_pk: int, package_matrix: int, user: int) -> None:
        package_activity_task = PackageActivityTask.objects.filter(pk=activity_task_pk).get()
        location_matrix_packages = LocationMatrixPackage.objects.filter(
            enabled=True,
            package_matrix_id=package_matrix,
            package_activity=package_activity_task.package_activity
        ).all()

        tasks = []

        if location_matrix_packages is not None:
            for location_matrix_package in location_matrix_packages:
                task_exists = Task.all_objects.filter(
                    location_matrix=location_matrix_package.location_matrix,
                    package_activity=location_matrix_package.package_activity,
                    package_activity_task=package_activity_task
                ).exists()

                if not task_exists:
                    tasks.append(
                        Task(
                            location_matrix=location_matrix_package.location_matrix,
                            building=location_matrix_package.location_matrix.building,
                            level=location_matrix_package.location_matrix.level,
                            area=location_matrix_package.location_matrix.area,
                            package_id=location_matrix_package.package_id,
                            package_activity=location_matrix_package.package_activity,
                            package_activity_task=package_activity_task,
                            user=user,
                            status=get_task_status(package_activity_task),
                            project_id=project_pk
                        )
                    )

        created_tasks = Task.objects.bulk_create(tasks, 500)
        create_task_updates(created_tasks)

        SubtaskEntityService().restore_for_shown_package_activity_task(activity_task_pk, project_pk)
        QualityIssueEntityService().restore_for_shown_package_activity_task(activity_task_pk, project_pk)

        Task.deleted_objects.filter(
            Exists(LocationMatrixPackage.objects.filter(
                package_activity_id=OuterRef('package_activity_id'),
                location_matrix_id=OuterRef('location_matrix_id'),
                enabled=True
            )),
            package_activity_task_id=activity_task_pk,
            location_matrix__deleted__isnull=True,
            location_matrix__project__id=project_pk
        ).update(deleted=None)

    def _set_date_of_approval(self, task: Task, update_data: dict) -> None:
        if task.status != Task.Statuses.ACCEPTED and update_data.get('status') == Task.Statuses.ACCEPTED:
            update_data['date_of_approval'] = pendulum.now().to_datetime_string()
