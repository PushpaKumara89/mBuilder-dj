# Generated by Django 3.1 on 2020-10-16 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_subtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='files',
            field=models.ManyToManyField(to='api.Media'),
        ),
    ]
