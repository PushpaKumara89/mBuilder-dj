from django.db import migrations

from api.models import AssetHandoverDocumentType


def add_asset_handover_document_type(*args, **kwargs):
    AssetHandoverDocumentType.objects.get_or_create(name='Asbuilt Drawing')
    AssetHandoverDocumentType.objects.get_or_create(name='Test Pack')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0148_auto_20211110_1055'),
    ]

    operations = [
        migrations.RunPython(add_asset_handover_document_type)
    ]
