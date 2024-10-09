from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_default_groups(*args, **kwargs):
    Group.objects.get_or_create(name='company_admin')
    Group.objects.get_or_create(name='admin')
    Group.objects.get_or_create(name='manager')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0002_change_managers_on_user_and_change_first_name_on_user')
    ]

    operations = [
        migrations.RunPython(add_default_groups)
    ]
