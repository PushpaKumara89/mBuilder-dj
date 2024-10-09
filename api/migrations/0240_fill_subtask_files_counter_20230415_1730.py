# Generated by Django 3.2.15 on 2023-04-15 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0239_add_task_files_counter_20230415_1238'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                with t as (
                    select s.id s_id, count(f.id) files_amount from subtasks s
                    inner join subtasks_files f on s.id = f.subtask_id
                    group by s.id
                )
                UPDATE subtasks SET files_count = t.files_amount
                from t
                where subtasks.id = t.s_id;
            """,
            reverse_sql="""
                UPDATE subtasks SET files_count = 0;
            """
        ),
        migrations.RunSQL(
            sql="""
                with t as (select subtask_id, count(suf.id) closed_files_count
                           from subtasks_updates su
                                    inner join subtasks_updates_files suf on su.id = suf.subtaskupdate_id
                           where su.new_data ->> 'status' = 'closed'
                           group by subtask_id)
                UPDATE subtasks
                SET closed_files_count = t.closed_files_count
                from t
                where subtasks.id = t.subtask_id;
            """,
            reverse_sql="""               
                UPDATE subtasks SET closed_files_count = 0;
            """
        ),
    ]
