# Generated by Django 3.2.4 on 2021-10-22 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0144_add_uid_for_package_handover_document_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='packagehandoverdocumentmedia',
            name='information',
            field=models.TextField(blank=True, null=True),
        ),
    ]
