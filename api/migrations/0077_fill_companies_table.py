# Generated by Django 2.0.5 on 2018-06-18 10:10

import pydash
from django.db import connection, migrations


def fill_company_table_from_existing_names(*args, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO companies(name, created_at, updated_at) SELECT DISTINCT company, NOW(), NOW() FROM auth_user WHERE company <> ''")


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0076_user_company_ref'),
    ]

    operations = [
        migrations.RunPython(fill_company_table_from_existing_names),
    ]
