# Generated by Django 3.1 on 2020-09-17 10:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20200917_0755'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='key_contacts',
            field=models.ManyToManyField(related_name='key_contacts', to=settings.AUTH_USER_MODEL),
        ),
    ]
