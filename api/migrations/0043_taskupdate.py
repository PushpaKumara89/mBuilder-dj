# Generated by Django 3.1.3 on 2020-11-07 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_auto_20201107_1024'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('old_data', models.JSONField()),
                ('new_data', models.JSONField()),
                ('files', models.ManyToManyField(to='api.Media')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tasks_updates',
            },
        ),
    ]
