# Generated by Django 3.1.3 on 2020-11-26 06:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_auto_20201117_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtask',
            name='due_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
