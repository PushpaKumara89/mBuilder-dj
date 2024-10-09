# Generated by Django 3.1.3 on 2020-11-13 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_recipient_subtaskupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_notifications_enabled', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'db_table': 'project_users',
            },
        ),
        migrations.AddConstraint(
            model_name='projectuser',
            constraint=models.UniqueConstraint(fields=('project', 'user'), name='project_user_unique'),
        ),
    ]
