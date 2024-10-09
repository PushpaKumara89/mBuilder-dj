from typing import List

from django.core.management.base import BaseCommand
from django.db import connection

from api.models import Project

class Command(BaseCommand):
    help = "Fill handover statistics by group company."
    options: dict
    only_asset_handover: bool
    only_package_handover: bool
    clear_asset_handover: bool
    clear_package_handover: bool
    clear_all: bool
    projects_ids: List[int]

    def add_arguments(self, parser):
        parser.add_argument('--only-asset-handover', action='store_true', help='Fill only asset handover statistics.')
        parser.add_argument('--only-package-handover', action='store_true', help='Fill only package handover statistics.')
        parser.add_argument('--clear-asset-handover', action='store_true', help='Clear rows only for asset handover statistics.')
        parser.add_argument('--clear-package-handover', action='store_true', help='Clear rows only for package handover statistics.')
        parser.add_argument('--clear-all', action='store_true', help='Clear rows for package and asset handover statistics.')
        parser.add_argument('--projects', action='append', help='Process only for projects.', nargs='+', type=int)

    def handle(self, *args, **options) -> None:
        self.init(options)
        projects = Project.objects.all()

        if self.only_asset_handover and self.only_package_handover:
            self.stdout.write(self.style.ERROR('You cannot use both options if you want to generate for all entities.'))
            return

        if self.clear_asset_handover and self.clear_package_handover:
            self.stdout.write(self.style.WARNING('You can use option --clear-all instead of --clear-asset-handover and --clear-package-handover together.'))

        if (self.clear_asset_handover or self.clear_package_handover) and self.clear_all:
            self.stdout.write(self.style.ERROR('Please use special options to clear certain entities or to clear everything, not both.'))
            return

        if self.projects_ids:
            projects = projects.filter(id__in=self.projects_ids)

        if self.projects_ids and projects.count() == 0:
            self.stdout.write(self.style.WARNING('There are no projects found with the given ids %s.' % self.projects_ids))
            return

        for project in projects:
            self.stdout.write(self.style.WARNING(f'Start operations on project {project.id}.'))

            self.__clear_statistics(project)
            self.__create_statistics(project)

            self.stdout.write(self.style.WARNING(f'Operations on project {project.id} has been finished.'))

    def __create_statistics(self, project: Project) -> None:
        if not any((self.clear_all, self.clear_asset_handover, self.clear_package_handover, self.only_asset_handover, self.only_package_handover)):
            self.__create_for_asset_handover(project.pk)
            self.__create_for_package_handover(project.pk)
        elif self.only_asset_handover or (self.clear_package_handover and self.only_asset_handover):
            self.__create_for_asset_handover(project.pk)
        elif self.only_package_handover or (self.clear_asset_handover and self.only_package_handover):
            self.__create_for_package_handover(project.pk)

    def __clear_statistics(self, project: Project) -> None:
        if not all((self.only_asset_handover, self.only_package_handover)):
            if self.clear_all or (self.clear_asset_handover and self.clear_package_handover):
                self.__clear_asset_handover(project.id)
                self.__clear_package_handover(project.id)
        if self.clear_asset_handover or (self.only_package_handover and self.clear_asset_handover):
            self.__clear_asset_handover(project.id)
        if self.clear_package_handover or (self.only_asset_handover and self.clear_package_handover):
            self.__clear_package_handover(project.id)

    def __create_for_asset_handover(self, project_pk: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start creating asset handover statistics for project {project_pk}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO asset_handover_statistics(asset_handover_document_id, project_id, group_id, company_id, 
                                                      required_files_count, in_progress_count, 
                                                      requesting_approval_count, accepted_count, contested_count,
                                                      requested_approval_rejected_count, removed_count, 
                                                      deleted, created_at, updated_at)
                SELECT ahdm.asset_handover_document_id,
                    %s                                                                                                                  AS project_id,
                    au.group_id                                                                                                         AS user_group,
                    au.company_id                                                                                                       AS user_company, 
                    MIN(number_required_files)                                                                                          AS required_files_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'in_progress' AND ahdm.deleted IS NULL )                            AS in_progress_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'requesting_approval' AND ahdm.deleted IS NULL )                    AS requesting_approval_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'accepted' AND ahdm.deleted IS NULL )                               AS accepted_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'contested' AND ahdm.deleted IS NULL )                              AS contested_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'requested_approval_rejected' AND ahdm.deleted IS NULL )            AS requested_approval_rejected_count,
                    COUNT(ahdm.status) FILTER ( WHERE ahdm.status = 'removed' AND ahdm.deleted IS NULL )                                AS removed_count,
                    CASE WHEN (bool_or(ah.deleted IS NOT NULL) OR bool_or(ahd.deleted IS NOT NULL)) THEN now() END                      AS deleted_at,
                    now(),
                    now()
            FROM asset_handover_document_media ahdm
                     INNER JOIN asset_handover_documents ahd ON ahd.id = ahdm.asset_handover_document_id
                     INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                     INNER JOIN (SELECT asset_handover_document_media_id,
                                        MIN(user_id) FILTER ( WHERE media_update.old_data = '{}' ) user_id
                                 FROM asset_handover_document_media_updates media_update
                                 GROUP BY asset_handover_document_media_id) ahdmu
                                ON ahdmu.asset_handover_document_media_id = ahdm.id
                     INNER JOIN auth_user au ON au.id = ahdmu.user_id
            WHERE ah.project_id = %s 
            GROUP BY ahdm.asset_handover_document_id, au.group_id, au.company_id;
            """, (project_pk, project_pk))

        self.stdout.write(self.style.WARNING(f'Asset handover statistics for project {project_pk} has been added.'))

    def __create_for_package_handover(self, project_pk: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start creating package handover statistics for project {project_pk}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO package_handover_statistics(package_handover_document_id, project_id, group_id, company_id, 
                                                        in_progress_count, requesting_approval_count, accepted_count, 
                                                        contested_count, requested_approval_rejected_count, 
                                                        removed_count, deleted, created_at, updated_at)
                SELECT phdm.package_handover_document_id,
                    %s                                                                                                                  AS project_id,
                    au.group_id                                                                                                         AS user_group,
                    au.company_id                                                                                                       AS user_company,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'in_progress' AND phdm.deleted IS NULL )                            AS in_progress_count,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'requesting_approval' AND phdm.deleted IS NULL )                    AS requesting_approval_count,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'accepted' AND phdm.deleted IS NULL )                               AS accepted_count,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'contested' AND phdm.deleted IS NULL )                              AS contested_count,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'requested_approval_rejected' AND phdm.deleted IS NULL )            AS requested_approval_rejected_count,
                    COUNT(phdm.status) FILTER ( WHERE phdm.status = 'removed' AND phdm.deleted IS NULL )                                AS removed_count,
                    CASE WHEN (bool_or(ph.deleted IS NOT NULL) OR bool_or(phd.deleted IS NOT NULL)) THEN now() END                      AS deleted_at,
                    now(),
                    now()
                FROM package_handover_document_media phdm
                     INNER JOIN package_handover_documents phd ON phd.id = phdm.package_handover_document_id
                     INNER JOIN package_handovers ph ON ph.id = phd.package_handover_id
                     INNER JOIN (SELECT package_handover_document_media_id,
                                        MIN(user_id) FILTER ( WHERE media_update.old_data = '{}' ) user_id
                                 FROM package_handover_document_media_updates media_update
                                 GROUP BY package_handover_document_media_id) phdmu
                                ON phdmu.package_handover_document_media_id = phdm.id
                     INNER JOIN auth_user au ON au.id = phdmu.user_id
            WHERE phd.project_id = %s 
            GROUP BY phdm.package_handover_document_id, au.group_id, au.company_id;
            """, (project_pk, project_pk))

        self.stdout.write(self.style.WARNING(f'Package handover statistics for project {project_pk} has been added.'))

    def __clear_asset_handover(self, project_id: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start clearing asset handover statistics for project {project_id}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM asset_handover_statistics WHERE project_id = %s AND group_id IS NOT NULL AND company_id IS NOT NULL 
            """, (project_id,))

        self.stdout.write(self.style.WARNING(f'Asset handover statistics for project {project_id} has been cleared.'))

    def __clear_package_handover(self, project_id: int) -> None:
        self.stdout.write(self.style.WARNING(f'Start clearing package handover statistics for project {project_id}.'))

        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM package_handover_statistics WHERE project_id = %s AND group_id IS NOT NULL AND company_id IS NOT NULL 
            """, (project_id,))

        self.stdout.write(self.style.WARNING(f'Package handover statistics for project {project_id} has been cleared.'))

    def init(self, options: dict) -> None:
        self.only_asset_handover = options['only_asset_handover']
        self.only_package_handover = options['only_package_handover']
        self.clear_asset_handover = options['clear_asset_handover']
        self.clear_package_handover = options['clear_package_handover']
        self.clear_all = options['clear_all']
        self.projects_ids = options['projects'][0] if options['projects'] else None
