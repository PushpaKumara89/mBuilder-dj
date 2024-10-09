from api.models import Task, PackageActivityTask
from api.utilities.tasks_utilities import get_task_status, create_task_updates


def restore_tasks_related_to_reinstated_location_matrix(location_matrices, user):
    for location_matrix in location_matrices:
        location_matrix_packages = location_matrix.locationmatrixpackage_set.filter(enabled=True).all()
        tasks = []
        restoring_tasks = []

        for location_matrix_package in location_matrix_packages:
            package_activity_tasks = PackageActivityTask.objects.filter(
                package_activity=location_matrix_package.package_activity
            ).all()

            for package_activity_task in package_activity_tasks:
                task = Task.all_objects.filter(
                    location_matrix=location_matrix_package.location_matrix,
                    package_activity=location_matrix_package.package_activity,
                    package_activity_task=package_activity_task
                ).first()

                if not task:
                    tasks.append(
                        Task(
                            building=location_matrix.building,
                            level=location_matrix.level,
                            area=location_matrix.area,
                            location_matrix=location_matrix,
                            package_id=location_matrix_package.package_id,
                            package_activity=location_matrix_package.package_activity,
                            package_activity_task=package_activity_task,
                            user=user,
                            status=get_task_status(package_activity_task),
                            project=location_matrix.project
                        )
                    )
                elif task.deleted:
                    task.deleted = None
                    restoring_tasks.append(task)

        if restoring_tasks:
            Task.objects.bulk_update(restoring_tasks, fields=['deleted'], batch_size=500)

        created_tasks = Task.objects.bulk_create(tasks, 500)
        create_task_updates(created_tasks)
