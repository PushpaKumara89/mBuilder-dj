from django.db.models import Q

from api.models import Task
from api.models import LocationMatrixPackage
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.services.subtask_entity_service import SubtaskEntityService
from api.utilities.tasks_utilities import get_task_status, create_task_updates


def restore_related_tasks_with_entities(location_matrix_package, user):
    restoring_tasks = Task.deleted_objects.filter(
        location_matrix=location_matrix_package.location_matrix_id,
        package_activity=location_matrix_package.package_activity_id,
    ).exclude(
        package_activity_task__packagematrixhiddenactivitytask__package_matrix=location_matrix_package.package_matrix
    )

    SubtaskEntityService().restore_from_tasks(restoring_tasks.all())
    QualityIssueEntityService().restore_from_tasks(restoring_tasks.all())

    existing_package_activity_tasks_ids = list(restoring_tasks.values_list('package_activity_task__pk', flat=True))
    restoring_tasks.update(package=location_matrix_package.package, deleted=None)

    package_activity_tasks = location_matrix_package.package_matrix.package_activity.packageactivitytask_set.exclude(
        Q(pk__in=existing_package_activity_tasks_ids) |
        Q(packagematrixhiddenactivitytask__package_matrix=location_matrix_package.package_matrix)
    ).all()

    tasks = []
    for package_activity_task in package_activity_tasks:
        if is_task_exist(location_matrix_package, package_activity_task):
            continue

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

    created_tasks = Task.objects.bulk_create(tasks, batch_size=500)

    create_task_updates(created_tasks)


def is_location_matrix_package_enabled(location_matrix_package) -> bool:
    return location_matrix_package['enabled']


def is_task_exist(location_matrix_package, package_activity_task) -> bool:
    return Task.objects.filter(
        location_matrix=location_matrix_package.location_matrix,
        package_activity=location_matrix_package.package_activity,
        package_activity_task=package_activity_task
    ).exists()


def is_package_activity_picked_in_project(location_matrix_package) -> bool:
    return LocationMatrixPackage.objects.filter(package_activity=location_matrix_package.package_activity,
                                                package_matrix__project=location_matrix_package.package_matrix.project,
                                                enabled=True).exists()
