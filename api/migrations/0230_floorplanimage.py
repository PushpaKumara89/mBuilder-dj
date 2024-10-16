# Generated by Django 3.2.15 on 2022-12-28 14:06
from django.core.management import call_command
from django.db import migrations, models
import django.db.models.deletion


def run_code(*args, **kwargs):
    call_command('convert_floor_plan_pdf_to_floor_plan_image')


def reverse_code(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0229_create_floor_plan_area_20221228_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='FloorPlanImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floor_plan_image', to='api.media')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.media')),
            ],
            options={
                'db_table': 'floor_plan_images',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.RunPython(code=run_code, reverse_code=reverse_code),
    ]
