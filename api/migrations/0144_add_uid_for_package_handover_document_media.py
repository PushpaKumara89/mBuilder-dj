# Generated by Django 3.2.4 on 2021-10-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0143_alter_packagehandoverdocumentmedia_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='packagehandoverdocumentmedia',
            name='uid',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, unique=True),
        ),
    ]
