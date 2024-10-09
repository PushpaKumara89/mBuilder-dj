# Generated by Django 3.2.4 on 2021-11-29 14:55

from django.db import migrations

from api.models import PackageHandoverDocumentType


def add_subcontractor_group_types(*args, **kwargs):
    PackageHandoverDocumentType.objects.get_or_create(name='Scope of Works or Systems', group_id=1)
    PackageHandoverDocumentType.objects.get_or_create(name='Asset Register', group_id=1)
    PackageHandoverDocumentType.objects.get_or_create(name='PPM Schedule', group_id=1)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0155_create_floor_plan_20211125_1434'),
    ]

    operations = [
        migrations.RunPython(add_subcontractor_group_types),
    ]
