# Generated by Django 3.2.4 on 2021-08-19 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0121_alter_subtask_location_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualityissueupdate',
            name='is_conflict',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subtaskupdate',
            name='is_conflict',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='taskupdate',
            name='is_conflict',
            field=models.BooleanField(default=False),
        ),
    ]
