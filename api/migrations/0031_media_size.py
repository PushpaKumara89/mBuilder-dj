# Generated by Django 3.1 on 2020-10-12 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_locationmatrixpackage_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='size',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
