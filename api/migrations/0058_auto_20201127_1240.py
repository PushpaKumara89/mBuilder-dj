# Generated by Django 3.1.3 on 2020-11-27 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_media_is_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='hash',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddConstraint(
            model_name='media',
            constraint=models.UniqueConstraint(condition=models.Q(deleted__isnull=True), fields=('hash',), name='api_media_hash_unique'),
        ),
    ]
