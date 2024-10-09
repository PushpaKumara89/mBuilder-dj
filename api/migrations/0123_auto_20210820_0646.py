# Generated by Django 3.2.4 on 2021-08-20 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0122_auto_20210819_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualityissue',
            name='local_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='subtask',
            name='local_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='local_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
