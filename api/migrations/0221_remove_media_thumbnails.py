# Generated by Django 3.2.15 on 2022-11-13 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0220_add_media_thumbnail_sizes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='thumbnails',
        ),
    ]
