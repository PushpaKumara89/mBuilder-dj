# Generated by Django 3.2.4 on 2021-07-30 06:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0117_delete_report'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('id',)},
        ),
    ]
