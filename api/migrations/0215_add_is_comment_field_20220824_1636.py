# Generated by Django 3.2.4 on 2022-08-24 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0214_appsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualityissueupdate',
            name='is_comment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subtaskupdate',
            name='is_comment',
            field=models.BooleanField(default=False),
        ),
    ]
