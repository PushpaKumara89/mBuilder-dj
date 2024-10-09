from collections import namedtuple

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from api.models import PackageMatrix, Task, Project, TaskUpdate


class Command(BaseCommand):
    help = "Create missing tasks for checked location matrix packages."

    def add_arguments(self, parser):
        parser.add_argument('project_pk', type=int)

    def handle(self, *args, **options):
        project = options['project_pk']

        try:
            project = Project.objects.get(pk=project)
        except Project.DoesNotExist:
            raise CommandError('Project "%s" does not exist.' % project)

        package_matrices = PackageMatrix.objects.filter(project=project).all()

        for package_matrix in package_matrices:
            self.stdout.write(self.style.WARNING('Start creating tasks for package matrix %s' % package_matrix.pk))

            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT DISTINCT pat.id pat_id, pat.is_not_applicable_status_by_default, pa.id pa_id, lm.id lm_id
                    FROM package_activity_tasks pat
                             INNER JOIN package_activities pa ON pat.package_activity_id = pa.id
                             INNER JOIN package_matrix pm ON pa.id = pm.package_activity_id
                             INNER JOIN location_matrix_packages lmp ON pa.id = lmp.package_activity_id
                             INNER JOIN location_matrix lm ON lmp.location_matrix_id = lm.id
                             INNER JOIN tasks t ON t.location_matrix_id = lm.id
                    WHERE pm.project_id = %s
                      AND pm.deleted IS NULL
                      AND lmp.enabled
                      AND lmp.deleted IS NULL
                      AND lm.deleted IS NULL
                      AND lm.project_id = %s
                      AND pa.deleted IS NULL
                      AND pat.deleted IS NULL
                      AND pm.id = %s
                      AND t.package_activity_task_id = pat.id
                      AND t.package_activity_id = pa.id
                      AND t.deleted IS NOT NULL
                      AND NOT EXISTS(SELECT id
                                     FROM package_matrix_hidden_activity_tasks pmhat
                                     WHERE pmhat.package_matrix_id = pm.id
                                       AND pmhat.package_activity_task_id = pat.id
                                       AND pmhat.deleted IS NULL);
                ''', [project.pk, project.pk, package_matrix.id])

                package_activity_tasks_without_qct = self.namedtuplefetchall(cursor)

            tasks = []

            for pat in package_activity_tasks_without_qct:
                task = Task.deleted_objects.filter(package_activity_id=pat.pa_id,
                                                   package_activity_task_id=pat.pat_id,
                                                   location_matrix_id=pat.lm_id).get()
                task.deleted = None
                tasks.append(task)

            Task.deleted_objects.bulk_update(tasks, ['deleted'], 100)

            TaskUpdate.all_objects.filter(task__in=tasks).update(deleted=None)

            self.stdout.write(self.style.WARNING('Task updates restored.'))

            self.stdout.write(self.style.WARNING('Created %s tasks' % len(tasks)))

            self.stdout.write(
                self.style.WARNING('Tasks creation for package matrix %s has been ended' % package_matrix.pk))

    def namedtuplefetchall(self, cursor):
        """Return all rows from a cursor as a namedtuple"""
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]
