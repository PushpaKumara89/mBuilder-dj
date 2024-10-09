import json
import os
from unittest import mock
from zipfile import ZipFile

import pendulum
from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.core.serializers import serialize
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import User, HandoverDocumentArchive, HandoverDocumentArchivePart
from api.queues.celery.handover_document_archive import generate_archive_part
from api.services.handover_document_archive_service import HandoverDocumentArchiveService
from api.tests.test import TestCase


class HandoverDocumentArchiveTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/handover_document_archive.json',
    ]
    file_system_storage = FileSystemStorage()
    WORKING_PROJECT = 5

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/media/troom.png'

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_temporary_zipfile_name',
                lambda *args, **kwargs: 'handover_document_archive_1.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._remove_temporary_file',
                lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob._blob_client.BlobClient.exists', lambda *args, **kwargs: False)
    @mock.patch('azure.storage.blob.BlobClient.append_block', lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob.BlobClient.create_append_blob', lambda *args, **kwargs: None)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', file_system_storage.open)
    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_archive_name',
                lambda *args, **kwargs: 'archive.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_sas_url',
                lambda *args, **kwargs: 'some-link.com/archive.zip')
    def test_get_completing_archive_by_superuser(self):
        completing_handover_document_archive = 1

        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')
        self.generate_and_save_fake_image('kroom.png')
        self.generate_and_save_fake_image('sroom.png')
        self.generate_and_save_fake_image('lroom.png')
        self.generate_and_save_fake_image('wroom.png')
        self.generate_and_save_fake_image('package_handover_media.png')

        archive_part = HandoverDocumentArchivePart.objects.filter(
            handover_document_archive_id=completing_handover_document_archive,
            status=HandoverDocumentArchivePart.Status.WAITING
        ).order_by('id').first()

        generate_archive_part(archive_part)

        self.assertDatabaseMissing(HandoverDocumentArchive,
                                   {'id': completing_handover_document_archive,
                                    'status': HandoverDocumentArchive.Status.IN_PROGRESS})

        self.assertDatabaseHas(HandoverDocumentArchive,
                               {'id': completing_handover_document_archive,
                                'status': HandoverDocumentArchive.Status.COMPLETED})

        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'handover_document_archive_id': completing_handover_document_archive,
                                    'status__in': [HandoverDocumentArchivePart.Status.FAILED,
                                                   HandoverDocumentArchivePart.Status.WAITING,
                                                   HandoverDocumentArchivePart.Status.SAVED]})

        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'handover_document_archive_id': completing_handover_document_archive,
                                    'status': HandoverDocumentArchivePart.Status.SENT,
                                    'media__isnull': True})

        with ZipFile('handover_document_archive_1.zip', 'r') as zip_archive:
            folder_structure = self.load_response_fixture('/handover_document_archive/completed_archive_folder_structure_assertion.json')
            archive_files = zip_archive.namelist()
            for file_path in folder_structure:
                self.assertIn(file_path, archive_files)

        os.remove('handover_document_archive_1.zip')

        self.assertEmailEquals([
            {
                'subject': 'MBuild - Handover Archive: (2 of 2 expected): Project 5 - 30/07/2020 - Files 3 - 4 of 10',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/handover_document_archive/completed_archive.html'
            }
        ])

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_temporary_zipfile_name',
                lambda *args, **kwargs: 'handover_document_archive_5.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._remove_temporary_file',
                lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob._blob_client.BlobClient.exists', lambda *args, **kwargs: False)
    @mock.patch('azure.storage.blob.BlobClient.append_block', lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob.BlobClient.create_append_blob', lambda *args, **kwargs: None)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', file_system_storage.open)
    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_archive_name',
                lambda *args, **kwargs: 'archive.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_sas_url',
                lambda *args, **kwargs: 'some-link.com/archive.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.process_next_part',
                lambda *args, **kwargs: None)
    def test_generate_archive_part_for_continued_archive_by_superuser(self):
        still_processing_handover_document_archive = 5

        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')
        self.generate_and_save_fake_image('kroom.png')
        self.generate_and_save_fake_image('sroom.png')
        self.generate_and_save_fake_image('lroom.png')
        self.generate_and_save_fake_image('wroom.png')
        self.generate_and_save_fake_image('package_handover_media.png')

        archive_part = HandoverDocumentArchivePart.objects.filter(
            handover_document_archive_id=still_processing_handover_document_archive,
            status=HandoverDocumentArchivePart.Status.WAITING
        ).order_by('id').first()

        generate_archive_part(archive_part)

        self.assertDatabaseHas(HandoverDocumentArchive,
                               {'id': still_processing_handover_document_archive,
                                'status': HandoverDocumentArchive.Status.IN_PROGRESS})

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'handover_document_archive_id': still_processing_handover_document_archive,
                                'status': HandoverDocumentArchivePart.Status.SENT})

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'handover_document_archive_id': still_processing_handover_document_archive,
                                'status': HandoverDocumentArchivePart.Status.WAITING})

        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'handover_document_archive_id': still_processing_handover_document_archive,
                                    'status': HandoverDocumentArchivePart.Status.SENT,
                                    'media__isnull': True})

        with ZipFile('handover_document_archive_5.zip', 'r') as zip_archive:
            folder_structure = self.load_response_fixture(
                '/handover_document_archive/continued_archive_folder_structure_assertion.json')
            archive_files = zip_archive.namelist()
            for file_path in folder_structure:
                self.assertIn(file_path, archive_files)

        os.remove('handover_document_archive_5.zip')

        self.assertEmailEquals([
            {
                'subject': 'MBuild - Handover Archive: (2 of 3 expected): Project 5 - 30/07/2020 - Files 3 - 6 of 10',
                'to': ['cool.subcontractor@gmail.com'],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/handover_document_archive/processing_archive.html'
            }
        ])

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_temporary_zipfile_name',
                lambda *args, **kwargs: 'handover_document_archive_6.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._remove_temporary_file',
                lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob._blob_client.BlobClient.exists', lambda *args, **kwargs: False)
    @mock.patch('azure.storage.blob.BlobClient.append_block', lambda *args, **kwargs: None)
    @mock.patch('azure.storage.blob.BlobClient.create_append_blob', lambda *args, **kwargs: None)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', file_system_storage.open)
    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_archive_name',
                lambda *args, **kwargs: 'archive.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService._get_sas_url',
                lambda *args, **kwargs: 'some-link.com/archive.zip')
    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.process_next_part',
                lambda *args, **kwargs: None)
    def test_get_first_archive_part_by_superuser(self):
        handover_document_archive_with_first_processing_part = 6

        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')
        self.generate_and_save_fake_image('kroom.png')
        self.generate_and_save_fake_image('sroom.png')
        self.generate_and_save_fake_image('lroom.png')
        self.generate_and_save_fake_image('wroom.png')
        self.generate_and_save_fake_image('package_handover_media.png')

        archive_part = HandoverDocumentArchivePart.objects.filter(
            handover_document_archive_id=handover_document_archive_with_first_processing_part,
            status=HandoverDocumentArchivePart.Status.WAITING
        ).order_by('id').first()

        generate_archive_part(archive_part)

        self.assertDatabaseHas(HandoverDocumentArchive,
                               {'id': handover_document_archive_with_first_processing_part,
                                'status': HandoverDocumentArchive.Status.IN_PROGRESS})

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'handover_document_archive_id': handover_document_archive_with_first_processing_part,
                                'status': HandoverDocumentArchivePart.Status.SENT})

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'handover_document_archive_id': handover_document_archive_with_first_processing_part,
                                'status': HandoverDocumentArchivePart.Status.WAITING})

        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'handover_document_archive_id': handover_document_archive_with_first_processing_part,
                                    'status': HandoverDocumentArchivePart.Status.SENT,
                                    'media__isnull': True})

        with ZipFile('handover_document_archive_6.zip', 'r') as zip_archive:
            folder_structure = self.load_response_fixture(
                '/handover_document_archive/first_archive_folder_structure_assertion.json')
            archive_files = zip_archive.namelist()
            for file_path in folder_structure:
                self.assertIn(file_path, archive_files)

        os.remove('handover_document_archive_6.zip')

        self.assertEmailEquals([
            {
                'subject': 'MBuild - Handover Archive: (1 of 2 expected): Project 5 - 30/07/2020 - Files 1 - 2 of 10',
                'to': ['cool.client@gmail.com'],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/handover_document_archive/started_archive.html'
            }
        ])

    def test_archive_name_generation(self):
        archive_part = HandoverDocumentArchivePart.objects.filter(
            status=HandoverDocumentArchivePart.Status.WAITING).order_by('id').first()
        archive_name = HandoverDocumentArchiveService()._get_archive_name(archive_part)
        self.assertEquals(archive_name, 'Project_5_2_of_3_2020-07-30_12-21-16_3_6.zip')

    def test_generation_archive_for_failed_part(self):
        archive_part = HandoverDocumentArchivePart.objects.filter(
            status=HandoverDocumentArchivePart.Status.FAILED).order_by('id').first()
        self.assertIsNone(HandoverDocumentArchiveService().create_archive_part_file(archive_part))
        self.assertDatabaseHas(HandoverDocumentArchivePart, {'id': archive_part.id,
                                                             'status': HandoverDocumentArchivePart.Status.FAILED,
                                                             'media__isnull': True})

    @mock.patch('sentry_sdk.hub.Hub.current.capture_exception', lambda *args, **kwargs: '123')
    def test_generate_archive_with_error(self):
        archive_part = HandoverDocumentArchivePart.objects.filter(
            status=HandoverDocumentArchivePart.Status.WAITING).order_by('id').first()

        with mock.patch('api.services.handover_document_archive_service.'
                        'HandoverDocumentArchiveService._get_asset_handover_archive_data') as m:
            m.side_effect = ValueError
            HandoverDocumentArchiveService().create_archive_part_file(archive_part)

            self.assertIsNone(HandoverDocumentArchiveService().create_archive_part_file(archive_part))
            self.assertDatabaseHas(HandoverDocumentArchivePart, {'id': archive_part.id,
                                                                 'status': HandoverDocumentArchivePart.Status.FAILED,
                                                                 'error_track_id': '123',
                                                                 'media__isnull': True})

    def test_initiate_generation_process_for_non_existing_project(self):
        user = User.objects.get(id=1)
        generation_started_at = pendulum.parse('2020-07-30T12:21:16.135Z')
        self.assertIsNone(HandoverDocumentArchiveService().initiate_generation_process(0, user, generation_started_at))
        self.assertDatabaseMissing(HandoverDocumentArchive, {'project': 0, 'user': user})

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.create_archive_part_file',
                lambda *args, **kwargs: None)
    def test_initiate_generation_process_for_existing_incomplete(self):
        user = User.objects.get(id=4)
        generation_started_at = pendulum.parse('2020-07-30T12:21:16.135Z')
        self.assertIsNone(HandoverDocumentArchiveService().initiate_generation_process(5, user, generation_started_at))
        self.assertEquals(HandoverDocumentArchive.objects.filter(project=5, user=user).count(), 1)

    def test_initiate_generation_process_without_parts(self):
        user = User.objects.get(id=4)
        generation_started_at = pendulum.parse('2020-07-30T12:21:16.135Z')
        self.assertIsNone(HandoverDocumentArchiveService().initiate_generation_process(1, user, generation_started_at))
        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'handover_document_archive__project': 1, 'handover_document_archive__user': user})
        self.assertDatabaseHas(HandoverDocumentArchive,
                               {'project': 1, 'user': user, 'status': HandoverDocumentArchive.Status.COMPLETED})

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.create_archive_part_file',
                lambda *args, **kwargs: None)
    def test_initial_generation(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_user(pk=3)
        response = self.client.get(url)

        self.assertOk(response)
        created_parts = serialize('json', HandoverDocumentArchivePart.objects.filter(id__gt=10))

        self.assertEqualsFixture(json.loads(created_parts),
                                 '/handover_document_archive/initial_generation.json')

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.initiate_generation_process',
                lambda *args, **kwargs: None)
    def test_get_archive_by_company_admin(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_company_admin()
        response = self.client.get(url)

        self.assertOk(response)

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.initiate_generation_process',
                lambda *args, **kwargs: None)
    def test_get_archive_by_project_admin(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_admin(project=5)
        response = self.client.get(url)

        self.assertOk(response)

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.initiate_generation_process',
                lambda *args, **kwargs: None)
    def test_get_archive_by_project_manager(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_manager(project=5)
        response = self.client.get(url)

        self.assertOk(response)

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.initiate_generation_process',
                lambda *args, **kwargs: None)
    def test_get_archive_by_project_client(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_client(project=5)
        response = self.client.get(url)

        self.assertOk(response)

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.initiate_generation_process',
                lambda *args, **kwargs: None)
    def test_get_archive_by_project_consultant(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_consultant(project=5)
        response = self.client.get(url)

        self.assertOk(response)

    def test_get_archive_by_project_subcontractor(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_subcontractor(project=5)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_archive_by_non_project_subcontractor(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_subcontractor(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_archive_by_non_project_client(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_client(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_archive_by_non_project_consultant(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_consultant(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_archive_by_non_project_manager(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_manager(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_archive_by_non_project_admin(self):
        url = reverse('handover_documents-generate_archive', kwargs={'project_pk': 5})

        self._log_in_as_admin(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.create_archive_part_file',
                lambda *args, **kwargs: None)
    def test_recover_failed_archive_part(self):
        call_command('recover_failed_archive_part', 1)
        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'id': 1, 'status': HandoverDocumentArchivePart.Status.WAITING,
                                'error_track_id__isnull': True})

    @mock.patch('api.services.handover_document_archive_service.HandoverDocumentArchiveService.create_archive_part_file',
                lambda *args, **kwargs: None)
    def test_recover_all_failed_archive_part(self):
        call_command('recover_failed_archive_part', all=True)
        self.assertDatabaseMissing(HandoverDocumentArchivePart,
                                   {'status': HandoverDocumentArchivePart.Status.FAILED,
                                    'error_track_id__isnull': False})

    def test_recover_failed_archive_part_without_all_options(self):
        call_command('recover_failed_archive_part')
        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'status': HandoverDocumentArchivePart.Status.FAILED,
                                'error_track_id__isnull': False})

    def test_recover_failed_archive_part_with_all_options(self):
        call_command('recover_failed_archive_part', 1, all=True)
        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'status': HandoverDocumentArchivePart.Status.FAILED,
                                'error_track_id__isnull': False})

    def test_recover_non_failed_archive_part(self):
        archive_part = 4
        before_changes = HandoverDocumentArchivePart.objects.get(id=archive_part)
        call_command('recover_failed_archive_part', archive_part)

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'status': HandoverDocumentArchivePart.Status.FAILED,
                                'error_track_id__isnull': False})

        after_changes = HandoverDocumentArchivePart.objects.get(id=archive_part)
        self.assertEquals(before_changes.status, after_changes.status)

    def test_recover_non_existing_failed_archive_part(self):
        call_command('recover_failed_archive_part', 123)

        self.assertDatabaseHas(HandoverDocumentArchivePart,
                               {'status': HandoverDocumentArchivePart.Status.FAILED,
                                'error_track_id__isnull': False})
