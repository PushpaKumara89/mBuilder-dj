from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_subcontructor_group(*args, **kwargs):
    Group.objects.get_or_create(name='subcontractor')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0052_subtask_estimation')
    ]

    operations = [
        migrations.RunPython(add_subcontructor_group)
    ]
