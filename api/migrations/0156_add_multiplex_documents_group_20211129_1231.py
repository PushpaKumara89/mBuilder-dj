# Generated by Django 3.2.4 on 2021-11-29 12:31

from django.db import migrations

from api.models import PackageHandoverDocumentGroup


def add_package_handover_document_group(*args, **kwargs):
    PackageHandoverDocumentGroup.objects.get_or_create(name='Multiplex Documents')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0155_create_floor_plan_20211125_1434'),
    ]

    operations = [
        migrations.RunPython(add_package_handover_document_group),
    ]
