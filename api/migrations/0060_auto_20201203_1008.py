# Generated by Django 3.1.3 on 2020-12-03 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0059_media_original_link'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='locationmatrix',
            name='location_matrix_unique',
        ),
    ]
