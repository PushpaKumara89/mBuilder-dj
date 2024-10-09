from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_client_group(*args, **kwargs):
    Group.objects.get_or_create(name='consultant')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0080_auto_20210317_0755')
    ]

    operations = [
        migrations.RunPython(add_client_group)
    ]
