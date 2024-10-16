# Generated by Django 3.1 on 2020-08-29 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_packageactivity'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageActivityTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('is_photo_required', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(db_index=True, default=0)),
            ],
            options={
                'db_table': 'package_activity_tasks',
            },
        ),
        migrations.AddConstraint(
            model_name='packageactivity',
            constraint=models.UniqueConstraint(condition=models.Q(deleted__isnull=True), fields=('name',), name='package_activity_unique_name_if_not_deleted'),
        ),
        migrations.AlterModelTable(
            name='packageactivity',
            table='package_activities',
        ),
        migrations.AddField(
            model_name='packageactivitytask',
            name='package_activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packageactivity'),
        ),
    ]
