from itertools import chain

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.models import Count

from api.models import Subtask, QualityIssue


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        quality_issues = QualityIssue.objects.annotate(subtasks_count=Count('subtask')).filter(subtasks_count__gt=1).order_by('id')

        duplicates = [
            (Subtask.objects
             .annotate(updates_count=Count('subtaskupdate'))
             .filter(quality_issue=qi)
             .order_by('-updates_count')[1:]
             .values_list('id', flat=True))
            for qi in quality_issues
        ]
        duplicates_ids = list(chain.from_iterable(duplicates))

        if duplicates_ids:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM subtasks_updates_recipients sur
                    USING subtasks_updates su
                    WHERE sur.subtaskupdate_id = su.id AND su.subtask_id IN %s;
                """, (tuple(duplicates_ids),))

                cursor.execute("""
                    DELETE FROM subtasks_updates_files suf
                    USING subtasks_updates su
                    WHERE suf.subtaskupdate_id = su.id AND su.subtask_id IN %s;
                """, (tuple(duplicates_ids),))

                cursor.execute("""
                    DELETE FROM subtasks_files sf
                    WHERE sf.subtask_id IN %s;
                """, (tuple(duplicates_ids),))

                cursor.execute("""
                    UPDATE subtasks SET last_update_id=null, last_confirmed_update_id=null WHERE id IN %s;
                """, (tuple(duplicates_ids),))

                cursor.execute("""
                    DELETE FROM subtasks_updates WHERE subtask_id IN %s;
                """, (tuple(duplicates_ids),))

                cursor.execute("""
                    DELETE FROM subtasks WHERE id IN %s;
                """, (tuple(duplicates_ids),))
