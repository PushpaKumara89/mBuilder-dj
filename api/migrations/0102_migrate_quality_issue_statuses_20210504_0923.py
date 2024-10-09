# Generated by Django 3.1.4 on 2021-05-04 09:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0101_auto_20210504_0923'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE quality_issue SET status = 'closed' WHERE status = 'closed_out';
        """),
        migrations.RunSQL("""
            UPDATE quality_issue_updates SET old_data = jsonb_set(old_data, '{status}', '"closed"') WHERE old_data ->> 'status' = 'closed_out';
        """),
        migrations.RunSQL("""
            UPDATE quality_issue_updates SET new_data = jsonb_set(new_data, '{status}', '"closed"') WHERE new_data ->> 'status' = 'closed_out';
        """),
    ]
