# Generated by Django 3.2.15 on 2023-04-29 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0250_add_subtask_status_weights_20230429_0925'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX subtasks_status_weight_for_staff 
                ON subtasks (status_weight_for_staff, building, level_number DESC, level_postfix, area, id)
                 WHERE (deleted IS NULL);
            """,
            reverse_sql="""
                DROP INDEX subtasks_status_weight_for_staff;
            """
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX subtasks_status_weight_for_subcontractor
                ON subtasks (status_weight_for_subcontractor, building, level_number DESC, level_postfix, area, id)
                 WHERE (deleted IS NULL);
            """,
            reverse_sql="""
                DROP INDEX subtasks_status_weight_for_subcontractor;
            """
        )
    ]
