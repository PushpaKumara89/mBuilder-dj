# Generated by Django 3.2.4 on 2021-12-15 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0164_merge_20211206_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='assethandoverdocumentmedia',
            name='uid',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
