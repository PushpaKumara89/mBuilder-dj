# Generated by Django 3.2.15 on 2023-05-02 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0253_add_location_matrix_level_parts_20230502_1435'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='locationmatrixpackage',
            constraint=models.Index(condition=models.Q(('deleted__isnull', True)), fields=['location_matrix', 'enabled'], name='location_matrix_packages_location_matrix_enabled_index'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.Index(condition=models.Q(('deleted__isnull', True)), fields=['project_id', 'user_id'], name='tasks_project_id_user_id_index'),
        ),
    ]
