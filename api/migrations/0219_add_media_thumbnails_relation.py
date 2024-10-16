# Generated by Django 3.2.15 on 2022-11-07 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0218_rename_projectsnapshotmediathumbnail_mediathumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediathumbnail',
            name='for_project_snapshot',
        ),
        migrations.AddField(
            model_name='media',
            name='thumbnails',
            field=models.ManyToManyField(related_name='_api_media_thumbnails_+', through='api.MediaThumbnail', to='api.Media'),
        ),
    ]
