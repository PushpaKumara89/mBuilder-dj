from django.core.management.base import BaseCommand
from django.db import connection, transaction
import pendulum


class Command(BaseCommand):
    help = "Create asset handovers for existing projects."

    def add_arguments(self, parser):
        parser.add_argument(
            '--truncate_existing',
            action='store_true',
            help='Truncate all existing tables for asset handover',
        )

    def handle(self, *args, **options):
        def get_location_matrix_packages_without_asset_handovers():
            cursor.execute('SELECT location_matrix_packages.location_matrix_id, location_matrix_packages.package_activity_id ' 
                           'FROM location_matrix_packages '
                           'LEFT JOIN asset_handovers '
                           'ON location_matrix_packages.location_matrix_id = asset_handovers.location_matrix_id AND '
                           'location_matrix_packages.package_activity_id = asset_handovers.package_activity_id '
                           'WHERE location_matrix_packages.enabled = true '
                           'AND location_matrix_packages.deleted IS NULL '
                           'AND asset_handovers.id is null')

            return cursor.fetchall()

        def get_asset_handover_document_types():
            cursor.execute('SELECT id FROM asset_handover_document_types')

            return cursor.fetchall()

        def truncate_existing_asset_handovers_asset_handover_documents_asset_handover_information():
            cursor.execute(
                'TRUNCATE asset_handovers, asset_handover_documents, asset_handover_information RESTART IDENTITY CASCADE')

        def create_asset_handover():
            cursor.execute(
                'INSERT INTO asset_handovers (location_matrix_id, package_activity_id, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING id',
                [
                    location_matrix_package[0],
                    location_matrix_package[1],
                    pendulum.now(),
                    pendulum.now()
                ])

            inserted_asset_handover_row = cursor.fetchone()

            return inserted_asset_handover_row[0]

        def create_asset_handover_documents():
            for asset_handover_document_type in asset_handover_document_types:
                cursor.execute(
                    'INSERT INTO asset_handover_documents (asset_handover_id, document_type_id, number_required_files, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)',
                    [
                        asset_handover_id,
                        asset_handover_document_type[0],
                        0,
                        pendulum.now(),
                        pendulum.now()
                    ]
                )

        def create_asset_handover_information():
            cursor.execute(
                'INSERT INTO asset_handover_information (asset_handover_id, created_at, updated_at) VALUES (%s, %s, %s)',
                [
                    asset_handover_id,
                    pendulum.now(),
                    pendulum.now()
                ])

        with connection.cursor() as cursor:
            if options['truncate_existing']:
                truncate_existing_asset_handovers_asset_handover_documents_asset_handover_information()

            self.stdout.write(self.style.WARNING('asset_handovers, asset_handover_documents and asset_handover_information has been truncated'))

            location_matrix_packages = get_location_matrix_packages_without_asset_handovers()
            count_location_matrix_packages = len(location_matrix_packages)

            self.stdout.write(self.style.WARNING('Found %s location matrix packages' % count_location_matrix_packages))

            asset_handover_document_types = get_asset_handover_document_types()

            self.stdout.write(self.style.WARNING('Found %s asset handover document types' % len(asset_handover_document_types)))

            for index, location_matrix_package in enumerate(location_matrix_packages, start=1):
                with transaction.atomic():
                    asset_handover_id = create_asset_handover()

                    create_asset_handover_documents()
                    create_asset_handover_information()

                self.stdout.write(self.style.WARNING('Asset handover for %s (%s of %s) location matrix package has been created' % (location_matrix_package[0], index, count_location_matrix_packages)))