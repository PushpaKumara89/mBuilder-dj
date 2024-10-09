from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Exists, OuterRef

from api.models import Task, LocationMatrixPackage


class Command(BaseCommand):
    help = "Remove tasks for unchecked LMP."

    def handle(self, *args, **options):
        tasks_count = Task.objects.filter(
            Exists(LocationMatrixPackage.objects.filter(
                location_matrix=OuterRef('location_matrix'),
                package_activity=OuterRef('package_activity'),
                enabled=False,
                deleted__isnull=True
            )),
            project__deleted__isnull=True
        ).count()

        self.stdout.write(self.style.WARNING('Start tasks removal with unchecked LMP.'))
        self.stdout.write(self.style.WARNING('Going to remove %s tasks.' % tasks_count))

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE tasks
                SET deleted = now()
                WHERE id IN (SELECT t.id
                             FROM tasks t
                                      LEFT JOIN location_matrix_packages lmp ON lmp.location_matrix_id = t.location_matrix_id
                                      INNER JOIN projects p ON p.id = t.project_id
                             WHERE t.package_activity_id = lmp.package_activity_id
                               AND p.deleted IS NULL
                               AND NOT lmp.enabled
                               AND t.deleted IS NULL)
            """)
