from api.utilities.tasks_utilities import get_task_status, create_task_updates

from api.models import Task, PackageActivityTask

from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.services.subtask_entity_service import SubtaskEntityService


def restore_tasks_related_to_reinstated_package_matrix(package_activity, location_matrix_packages: list, location_matrix, user):
    deleted_tasks = Task.deleted_objects.filter(
        location_matrix=location_matrix,
        package_activity=package_activity
    ).all()

    SubtaskEntityService().restore_from_tasks(deleted_tasks)
    QualityIssueEntityService().restore_from_tasks(deleted_tasks)

    deleted_tasks_updates = {
        'deleted': None,
    }

    if location_matrix_packages:
        deleted_tasks_updates['package'] = location_matrix_packages[0].package

    deleted_tasks.update(**deleted_tasks_updates)

    package_activity_tasks = PackageActivityTask.objects.filter(package_activity=package_activity).all()

    tasks = []
    restoring_tasks = []

    for location_matrix_package in location_matrix_packages:
        for package_activity_task in package_activity_tasks:
            task = Task.all_objects.filter(
                location_matrix=location_matrix_package.location_matrix,
                package_activity=location_matrix_package.package_activity,
                package_activity_task=package_activity_task
            ).first()

            if not task:
                tasks.append(
                    Task(
                        location_matrix=location_matrix_package.location_matrix,
                        building=location_matrix_package.location_matrix.building,
                        level=location_matrix_package.location_matrix.level,
                        area=location_matrix_package.location_matrix.area,
                        package=location_matrix_package.package,
                        package_activity=location_matrix_package.package_activity,
                        package_activity_task=package_activity_task,
                        user=user,
                        status=get_task_status(package_activity_task),
                        project=location_matrix_package.location_matrix.project
                    )
                )
            elif task.deleted:
                task.deleted = None
                restoring_tasks.append(task)

    if restoring_tasks:
        Task.objects.bulk_update(restoring_tasks, fields=['deleted'], batch_size=500)

    created_tasks = Task.objects.bulk_create(tasks, 500)

    create_task_updates(created_tasks)

