from django.db import migrations

from api.models import PackageMatrix, PackageMatrixHiddenActivityTask, PackageActivityTask, Task


def get_activity_tasks():
    ids = Task.all_objects.distinct().order_by('-id').values_list('package_activity_task_id', flat=True)
    hidden_ids = PackageMatrixHiddenActivityTask.objects.distinct().values_list('package_activity_task_id', flat=True)
    ids = set(list(ids) + list(hidden_ids))

    return PackageActivityTask.objects.exclude(pk__in=ids).values('package_activity_id', 'id')


def get_package_matrices(activity_ids):
    return PackageMatrix.all_objects.filter(package_activity_id__in=activity_ids).distinct().all()


def hide_unused_package_activity_tasks(*args, **kwargs):
    hidden_tasks = []
    activity_tasks = get_activity_tasks()
    package_activity_ids = [activity_task.package_activity_id for activity_task in activity_tasks]
    package_matrices = get_package_matrices(package_activity_ids)

    for activity_task in activity_tasks:
        matrices = package_matrices.filter(package_activity_id=activity_task.package_activity_id)

        for matrix in matrices:
            hidden_tasks.append(PackageMatrixHiddenActivityTask(
                package_matrix=matrix,
                package_activity_task_id=activity_task.id
            ))

    PackageMatrixHiddenActivityTask.objects.bulk_create(hidden_tasks, 100)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0068_auto_20210123_1530'),
    ]

    operations = [
        migrations.RunPython(hide_unused_package_activity_tasks)
    ]
