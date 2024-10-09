from django.db import migrations
from django.db.models import Exists, OuterRef

from api.models import PackageMatrixHiddenActivityTask, PackageActivityTask, Task


def delete_qct_with_hidden_related_tasks(*args, **kwargs):
    activity_tasks = PackageActivityTask.all_objects.filter(Exists(
        PackageMatrixHiddenActivityTask.all_objects.filter(package_activity_task_id=OuterRef('id'))
    )).all().values('id')

    for activity_task in activity_tasks:
        hidden_activity_tasks = activity_task.packagematrixhiddenactivitytask_set.all()
        for hidden_activity_task in hidden_activity_tasks:
            Task.objects.filter(
                package_activity_task=activity_task,
                location_matrix__project_id=hidden_activity_task.package_matrix.project_id
            ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_hide_unused_package_activity_tasks'),
    ]

    operations = [
        migrations.RunPython(delete_qct_with_hidden_related_tasks)
    ]
