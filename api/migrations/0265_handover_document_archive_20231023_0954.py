# Generated by Django 3.2.15 on 2023-10-23 09:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0264_change_floor_plan_constraint_20231004_1114'),
    ]

    operations = [
        migrations.CreateModel(
            name='HandoverDocumentArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('generation_started_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('in_progress', 'In progress'), ('completed', 'Completed')], default='in_progress', max_length=11)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'handover_document_archives',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HandoverDocumentArchivePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset_handover_media_range', models.JSONField(default=dict)),
                ('package_handover_media_range', models.JSONField(default=dict)),
                ('in_range_files_count', models.IntegerField(default=0)),
                ('total_files_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('running', 'Running'), ('failed', 'Failed'), ('saved', 'Saved'), ('sent', 'Sent')], default='waiting', max_length=7)),
                ('handover_document_archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.handoverdocumentarchive')),
                ('media', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.media')),
                ('error_track_id', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'handover_document_archive_parts',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='handoverdocumentarchive',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'completed'), _negated=True), fields=('project', 'user'), name='handover_document_archives_uniqueness'),
        ),
    ]
