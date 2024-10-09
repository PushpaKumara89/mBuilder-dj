# Generated by Django 3.2.4 on 2022-04-01 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0183_assethandover_project'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='assethandover',
            index=models.Index(fields=['project', 'package_activity', 'deleted'], name='asset_handovers_ihe6oz_index'),
        ),
    ]
