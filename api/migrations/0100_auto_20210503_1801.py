# Generated by Django 3.1.4 on 2021-05-03 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0099_merge_20210503_1114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qualityissue',
            old_name='old_quality_issue_id',
            new_name='old_quality_issue',
        ),
    ]
