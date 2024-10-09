from typing import List

from django.core.management.base import BaseCommand
from django.db import connection

from api.models import Project

class Command(BaseCommand):
    help = "Fill initial handover statistics."
    only_asset_handover: bool
    only_package_handover: bool
    projects_ids: List[int]

    def add_arguments(self, parser):
        parser.add_argument('--only-asset-handover', action='store_true', help='Fill only asset handover statistics.')
        parser.add_argument('--only-package-handover', action='store_true', help='Fill only package handover statistics.')
        parser.add_argument('--projects', action='append', help='Process only for projects.', nargs='+', type=int)

    def handle(self, *args, **options) -> None:
        self.init(options)
        projects = Project.objects.all()

        if self.only_asset_handover and self.only_package_handover:
            self.stdout.write(self.style.ERROR('You cannot use both options if you want to generate for all entities.'))
            return

        if self.projects_ids:
            projects = projects.filter(id__in=self.projects_ids)

        if self.projects_ids and projects.count() == 0:
            self.stdout.write(self.style.WARNING('There are no projects found with the given ids %s.' % self.projects_ids))
            return

        for project in projects:
            self.stdout.write(self.style.WARNING(f'Start operations on project {project.id}.'))

            self.__create_statistics(project)

            self.stdout.write(self.style.WARNING(f'Operations on project {project.id} has been finished.'))

    def __create_statistics(self, project: Project) -> None:
        if self.only_asset_handover:
            self.__create_for_asset_handover(project.pk)
        elif self.only_package_handover:
            self.__create_for_package_handover(project.pk)
        else:
            self.__create_for_asset_handover(project.pk)
            self.__create_for_package_handover(project.pk)

    def __create_for_asset_handover(self, project_pk: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start creating asset handover statistics for project {project_pk}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO asset_handover_statistics(asset_handover_document_id, project_id, group_id, company_id,
                                      required_files_count, in_progress_count,
                                      requesting_approval_count, accepted_count, contested_count,
                                      requested_approval_rejected_count, removed_count,
                                      deleted, created_at, updated_at)
                SELECT ahd.id,
                       %s,
                       null,
                       null,
                       ahd.number_required_files,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       CASE WHEN ah.deleted IS NOT NULL OR ahd.deleted IS NOT NULL THEN now() END,
                       now(),
                       now()
                FROM asset_handover_documents ahd
                INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                WHERE ah.project_id = %s AND NOT exists(SELECT (1) FROM asset_handover_statistics ahs1 WHERE asset_handover_document_id = ahd.id AND ahs1.group_id IS NULL AND ahs1.company_id IS NULL)
            """, (project_pk, project_pk))

        self.stdout.write(self.style.WARNING(f'Asset handover statistics for project {project_pk} has been added.'))

    def __create_for_package_handover(self, project_pk: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start creating package handover statistics for project {project_pk}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO package_handover_statistics(package_handover_document_id, project_id, group_id, company_id,
                                                        in_progress_count, requesting_approval_count, accepted_count,
                                                        contested_count, requested_approval_rejected_count, removed_count,
                                                        deleted, created_at, updated_at)
                SELECT phd.id,
                       %s,
                       null,
                       null,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       CASE WHEN ph.deleted IS NOT NULL OR phd.deleted IS NOT NULL THEN now() END,
                       now(),
                       now()
                FROM package_handover_documents phd
                         INNER JOIN package_handovers ph ON ph.id = phd.package_handover_id
                WHERE phd.project_id = %s AND NOT exists(SELECT (1) FROM package_handover_statistics phs1 WHERE package_handover_document_id = phd.id AND phs1.group_id IS NULL AND phs1.company_id IS NULL);

            """, (project_pk, project_pk))

        self.stdout.write(self.style.WARNING(f'Package handover statistics for project {project_pk} has been added.'))

    def init(self, options: dict) -> None:
        self.only_asset_handover = options['only_asset_handover']
        self.only_package_handover = options['only_package_handover']
        self.projects_ids = options['projects'][0] if options['projects'] else None
