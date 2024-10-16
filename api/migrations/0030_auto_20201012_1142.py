# Generated by Django 3.1 on 2020-10-12 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from api.models import Task


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20201008_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(max_length=255)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('not_applicable', 'Not Applicable'), ('not_verified', 'Not Verified'), ('outstanding', 'Outstanding'), ('part_complete', 'Part Complete'), ('rejected', 'Rejected')], max_length=255, default=Task.Statuses.OUTSTANDING.value)),
            ],
            options={
                'db_table': 'tasks',
            },
        ),
        migrations.AddConstraint(
            model_name='packagematrix',
            constraint=models.UniqueConstraint(fields=('project', 'package_activity'), name='package_matrix_unique_activity'),
        ),
        migrations.AddField(
            model_name='task',
            name='location_matrix',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locationmatrix'),
        ),
        migrations.AddField(
            model_name='task',
            name='package_activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packageactivity'),
        ),
        migrations.AddField(
            model_name='task',
            name='package_activity_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packageactivitytask'),
        ),
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.UniqueConstraint(fields=('package_activity', 'package_activity_task', 'location_matrix'), name='tasks_uniqueness'),
        ),
    ]
