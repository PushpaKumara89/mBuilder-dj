# Generated by Django 3.1 on 2020-09-24 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_project_key_contacts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packageactivitytask',
            name='photo_requirement_comment',
            field=models.TextField(default='Comment'),
            preserve_default=False,
        ),
    ]
