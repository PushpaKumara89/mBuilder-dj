# Generated by Django 3.2.4 on 2021-11-29 12:32

from django.db import migrations

from api.models import PackageHandoverDocumentType, PackageHandoverDocumentGroup


def add_package_handover_document_types(*args, **kwargs):
    group = PackageHandoverDocumentGroup.objects.filter(name='H&S Consultant Documents').get()
    PackageHandoverDocumentType.objects.get_or_create(name='Fire and Emergency File', group_id=group.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0162_merge_20211203_0654'),
    ]

    operations = [
        migrations.RunPython(add_package_handover_document_types),
    ]
