# Generated by Django 3.2.15 on 2023-02-28 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0235_floor_plan_revision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packageactivity',
            name='description_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='package_activity_description_image', to='api.media'),
        ),
    ]
