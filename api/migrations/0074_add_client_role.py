from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_client_group(*args, **kwargs):
    Group.objects.get_or_create(name='client')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0073_auto_20210315_0640')
    ]

    operations = [
        migrations.RunPython(add_client_group)
    ]
