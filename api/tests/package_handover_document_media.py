from unittest import mock
from unittest.mock import patch
from zipfile import ZipFile

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.urls import reverse

from api.models import Media
from api.models.package_handover import PackageHandoverDocumentMedia, PackageHandoverDocumentMediaUpdate
from api.services.handover_document_media_download_service import HandoverDocumentMediaDownloadService
from api.tests.test import TestCase, data_provider


class PackageHandoverDocumentMediaTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/package_handovers.json',
        'api/tests/fixtures/dumps/package_handover_document.json'
    ]
    fss = FileSystemStorage()

    def mock_generated_archive_name(self):
        return 'archive.zip'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_consultant_package_handover_document_media.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': superuser.pk,
                'package_handover_document_media': response.data['id'],
                'old_data': {},
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'package_handover_media.png')
    def test_bulk_create_by_superuser(self):
        self.generate_and_save_fake_image('package_handover_media.png')

        superuser = self._get_superuser()
        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_consultant_package_handover_document_media.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertCreated(response)
        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/bulk_created_package_handover_document_media_by_superuser.json')
        self._exclude_expanded_fields_from_response(response)
        for package_handover_document_media in response.data:
            self.assertDatabaseHas(PackageHandoverDocumentMedia, {**package_handover_document_media})

    def test_create_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_staff.pk,
                'package_handover_document_media': response.data['id'],
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'package_handover_media.png')
    def test_bulk_create_by_staff(self):
        self.generate_and_save_fake_image('package_handover_media.png')

        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)
        self.assertCreated(response)
        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/bulk_created_package_handover_document_media_by_staff.json')
        self._exclude_expanded_fields_from_response(response)
        for package_handover_document_media in response.data:
            self.assertDatabaseHas(PackageHandoverDocumentMedia, {**package_handover_document_media})

    def test_create_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_subcontractor_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_subcontractor.pk,
                'package_handover_document_media': response.data['id'],
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'package_handover_media.png')
    def test_bulk_create_by_subcontractor(self):
        self.generate_and_save_fake_image('package_handover_media.png')

        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_subcontractor_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertCreated(response)
        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/bulk_created_package_handover_document_media_by_subcontractor.json')
        self._exclude_expanded_fields_from_response(response)
        for package_handover_document_media in response.data:
            self.assertDatabaseHas(PackageHandoverDocumentMedia, {**package_handover_document_media})

    def test_forbid_create_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertForbidden(response)

    def test_create_by_subcontractor_from_not_whitelisted_company(self):
        project_subcontractor = self._get_subcontractor(company=1, project=5)
        self.force_login_user(project_subcontractor.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_subcontractor_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You\'re not allowed to create media."]}')

    def test_forbid_bulk_create_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertForbidden(response)

    def test_create_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_consultant.pk,
                'package_handover_document_media': response.data['id'],
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'package_handover_media.png')
    def test_bulk_create_by_consultant(self):
        self.generate_and_save_fake_image('package_handover_media.png')

        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_consultant_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertCreated(response)
        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/bulk_created_package_handover_document_media_by_consultant.json')
        self._exclude_expanded_fields_from_response(response)
        for package_handover_document_media in response.data:
            self.assertDatabaseHas(PackageHandoverDocumentMedia, {**package_handover_document_media})

    def test_forbid_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/create_subcontractor_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/', new_package_handover_document_media)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        new_package_handover_document_media = self.load_request_fixture('/package_handover_document_media/bulk_create_subcontractor_package_handover_document_media.json')

        response = self.client.post('/api/projects/5/package-handover-document-media/bulk/', new_package_handover_document_media)

        self.assertForbidden(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/package-handover-document-media/1/')

        self.assertNoContent(response)

    def test_delete_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.delete('/api/projects/5/package-handover-document-media/1/')

        self.assertNoContent(response)

    def test_delete_by_admin(self):
        self._log_in_as_admin(project=5)

        response = self.client.delete('/api/projects/5/package-handover-document-media/1/')

        self.assertNoContent(response)

    def test_forbid_delete_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.delete('/api/projects/6/package-handover-document-media/4/')

        self.assertForbidden(response)

    def test_delete_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.delete('/api/projects/5/package-handover-document-media/1/')

        self.assertNoContent(response)

    def test_forbid_delete_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.delete('/api/projects/5/package-handover-document-media/3/')

        self.assertForbidden(response)

    def test_delete_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.delete('/api/projects/5/package-handover-document-media/13/')

        self.assertNoContent(response)

    def test_forbid_delete_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.delete('/api/projects/5/package-handover-document-media/1/')

        self.assertForbidden(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/get_package_handover_document_media.json')

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    def test_forbid_download_by_non_project_admin(self):
        non_project_admin = self._get_admin(~Q(project=5))
        self.force_login_user(non_project_admin.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertForbidden(response)

    def test_forbid_download_by_non_project_manager(self):
        non_project_manager = self._get_manager(~Q(project=5))
        self.force_login_user(non_project_manager.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertForbidden(response)

    def test_forbid_download_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertForbidden(response)

    def test_forbid_download_by_non_project_consultant(self):
        non_project_consultant = self._get_consultant(~Q(project=5))
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertForbidden(response)

    def test_forbid_download_by_non_project_client(self):
        non_project_client = self._get_client(~Q(project=5))
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertForbidden(response)

    def test_forbid_download_in_not_allowed_status_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/2/download/')

        self.assertForbidden(response)

    def test_unauthorized_download(self):
        response = self.client.get('/api/projects/5/package-handover-document-media/1/download/')

        self.assertUnauthorized(response)

    def test_get_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/get_package_handover_document_media.json')

    def test_get_by_staff_with_expanded_last_status_change_update(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/', {'expand': ['expanded_last_status_change_update']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data,
            '/package_handover_document_media/get_package_handover_document_media_with_expanded_last_status_change_update.json')

    def test_forbid_get_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/6/package-handover-document-media/4/')

        self.assertForbidden(response)

    def test_get_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/get_package_handover_document_media.json')

    def test_forbid_get_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/3/')

        self.assertForbidden(response)

    def test_get_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/13/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media/get_consultant_package_handover_document_media.json')

    def test_forbid_get_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/')

        self.assertForbidden(response)

    def get_filters_for_superuser(self):
        return (
            (
                {'all': True, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_all_by_superuser.json',
                {'project_pk': 5}
            ),
            (
                {'page': 1, 'per_page': 2, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_page_by_superuser.json',
                {'project_pk': 5}
            ),
            (
                {'all': True, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_all_from_other_project_by_superuser.json',
                {'project_pk': 6}
            ),
            (
                {'search': 'sfs', 'use_limit_offset_pagination': True},
                '/package_handover_document_media/search_by_uid.json',
                {'project_pk': 5}
            ),
            (
                {'search': 'still', 'use_limit_offset_pagination': True},
                '/package_handover_document_media/search_by_information.json',
                {'project_pk': 5}
            ),
            (
                {'search': 'broom', 'use_limit_offset_pagination': True},
                '/package_handover_document_media/search_by_media_name.json',
                {'project_pk': 5}
            ),
            (
                {'use_limit_offset_pagination': True, 'expand': ['expanded_package_handover_document.expanded_package_activity']},
                '/package_handover_document_media/search_with_expanded_package_activity.json',
                {'project_pk': 5}
            ),
            (
                {'company': [2]},
                '/package_handover_document_media/filter_by_company.json',
                {'project_pk': 5}
            ),
        )

    @data_provider(get_filters_for_superuser)
    def test_search(self, filters, fixture, params):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/%s/package-handover-document-media/' % params['project_pk'], filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_staff(self):
        return (
            (
                {'all': True, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_all_by_staff.json'
            ),
            (
                {'page': 1, 'per_page': 2, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_page_by_staff.json',
            ),
        )

    @data_provider(get_filters_for_staff)
    def test_search_by_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_subcontractor(self):
        return (
            (
                {'all': True, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_all_by_subcontractor.json'
            ),
            (
                {'page': 1, 'per_page': 2, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_page_by_subcontractor.json',
            ),
        )

    @data_provider(get_filters_for_subcontractor)
    def test_search_by_subcontractor(self, filters, fixture):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_consultant(self):
        return (
            (
                {'all': True, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_all_by_consultant.json'
            ),
            (
                {'page': 1, 'per_page': 2, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/get_page_by_consultant.json',
            ),
            (
                {'package_handover_document': 2, 'use_limit_offset_pagination': True},
                '/package_handover_document_media/filter_by_package_handover_document.json',
            ),
            (
                {'package_handover_document_type': [1, 9], 'use_limit_offset_pagination': True},
                '/package_handover_document_media/filter_by_package_handover_document_type.json',
            ),
            (
                {'package_handover_document_group': [1, 2, 3, 4], 'use_limit_offset_pagination': True},
                '/package_handover_document_media/filter_by_package_handover_document_group.json',
            ),
            (
                {'package_activity': [1, 2], 'use_limit_offset_pagination': True},
                '/package_handover_document_media/filter_by_package_activity.json',
            ),
            (
                {'package': [4], 'use_limit_offset_pagination': True},
                '/package_handover_document_media/filter_by_package.json',
            ),
        )

    @data_provider(get_filters_for_consultant)
    def test_search_by_consultant(self, filters, fixture):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_search_package_activities_with_package_handover_documents(self):
        return (
            (
                {'has_package_handover_documents': True, 'project': 5, 'package': 4},
                '/package_handover_document_media/get_package_activities_with_package_handover_documents_by_superuser.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'has_package_handover_documents': True, 'project': 5, 'package': 3},
                '/package_handover_document_media/get_package_activities_with_package_handover_documents_by_consultant.json',
                {'user_pk': self._get_consultant(project=5).pk}
            ),
            (
                {'has_package_handover_documents': True, 'project': 5, 'package': 3},
                '/package_handover_document_media/get_package_activities_with_package_handover_documents_by_subcontractor.json',
                {'user_pk': self._get_subcontractor(project=5).pk}
            ),
        )

    @data_provider(get_filters_for_search_package_activities_with_package_handover_documents)
    def test_search_package_activities_with_package_handover_documents(self, filters, fixture, params):
        self.force_login_user(params['user_pk'])
        response = self.client.get('/api/package-activities/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_information_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handovers/information-csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover_document_media/handover_information_csv_report_created.html'
            }
        ])

    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch.object(HandoverDocumentMediaDownloadService, '_HandoverDocumentMediaDownloadService__generate_archive_name', mock_generated_archive_name)
    def test_get_information_csv_by_superuser(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        data = {'package_handover_document_media': [1, 2]}
        url = reverse('package_handover_document_media_batch', kwargs={'project_pk': 5})

        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.post(url, data)

        self.assertOk(response)
        self.assertDatabaseHas(Media, {'name': 'archive.zip'})

        with ZipFile('media/archive.zip', 'r') as zip_archive:
            media_names = list(
                Media.objects.filter(packagehandoverdocumentmedia__id__in=data['package_handover_document_media']).values_list('name', flat=True))
            files_namelist = zip_archive.namelist()
            for media_name in media_names:
                self.assertIn(media_name, files_namelist)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report - Archive of selected files',
                'to': [superuser.email],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/package_handover_document_media/notify_about_ability_to_download_archive.html'
            }
        ])

    def test_archive_file_name_generation(self):
        date_mock = pendulum.datetime(2020, 1, 1, 00, 00)
        pendulum.set_test_now(date_mock)
        service = HandoverDocumentMediaDownloadService()
        expected = 'handover_document_report_%s.zip' % date_mock.to_datetime_string()
        actual = service._HandoverDocumentMediaDownloadService__generate_archive_name()

        self.assertEquals(expected, actual)
