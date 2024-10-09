from django.core.management import call_command
from django.db import migrations


def remove_users_from_projects(*args, **kwargs):
    call_command('remove_users_company_admin_from_projects')


def reverse_code(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0226_add_asset_registry_for_all_projects_20221214_0603'),
    ]

    operations = [
        migrations.RunPython(code=remove_users_from_projects, reverse_code=reverse_code),
    ]
