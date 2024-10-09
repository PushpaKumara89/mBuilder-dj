from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0166_auto_20220113_0659'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHandoverStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('required_files_count', models.IntegerField(default=0)),
                ('uploaded_files_count', models.IntegerField(default=0)),
                ('filled_info_count', models.IntegerField(default=0)),
                ('total_info_count', models.IntegerField(default=0)),
                ('statistics_by_statuses', models.JSONField(default=dict)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
            options={
                'db_table': 'asset_handover_statistics',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='assethandoverstatistics',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('project',), name='asset_handover_statistics_unique'),
        ),
    ]
