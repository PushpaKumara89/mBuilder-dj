# Generated by Django 3.1.4 on 2021-03-09 05:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0070_delete_qct_with_hidden_related_tasks'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfflineMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'offline_mode',
            },
        ),
        migrations.AddConstraint(
            model_name='offlinemode',
            constraint=models.UniqueConstraint(fields=('project', 'user'), name='offline_mode_uniqueness'),
        ),
    ]
