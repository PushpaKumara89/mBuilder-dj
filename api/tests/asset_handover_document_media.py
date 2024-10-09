from unittest import mock
from unittest.mock import patch
from zipfile import ZipFile

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import User, AssetHandoverDocumentMedia, AssetHandoverDocumentMediaUpdate, AssetHandoverDocumentType, \
    Media
from api.services.handover_document_media_download_service import HandoverDocumentMediaDownloadService
from api.tests.test import TestCase, data_provider


class AssetHandoverDocumentMediaTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/asset_handover_document_media.json']
    fss = FileSystemStorage()

    def mock_generated_archive_name(self):
        return 'archive.zip'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_company_admin.json',
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                {'all': True, 'sort': 'id', 'asset_handover_document': 2, 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/filter_by_asset_handover_document.json',
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_project_admin.json',
                {'groups': User.Group.ADMIN.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_project_manager.json',
                {'groups': User.Group.MANAGER.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_project_client.json',
                {'groups': User.Group.CLIENT.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_project_subcontractor.json',
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5, 'company': 1}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_by_project_consultant.json',
                {'groups': User.Group.CONSULTANT.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id', 'asset_handover': 1, 'asset_handover_document_type': 1, 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_asset_handover.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'asset_handover_document_type': 1, 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_asset_handover_document_type.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'status': [AssetHandoverDocumentMedia.Status.IN_PROGRESS, AssetHandoverDocumentMedia.Status.CONTESTED], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_statuses.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'building': ['Building A'], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_building.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'level': ['7A'], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_level.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'area': ['Hall'], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_area.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'package_activity': [1], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_package_activity.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'package': [4], 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/get_all_for_package.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'search': 'thing', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/search_by_uid.json',
                {'is_superuser': True},
            ),
            (
                {'all': True, 'sort': 'id', 'search': 'oom', 'use_limit_offset_pagination': True},
                '/asset_handover_document_media/search_by_media_name.json',
                {'is_superuser': True},
            ),
            (
                {'company': [8]},
                '/asset_handover_document_media/filter_by_company.json',
                {'is_superuser': True},
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_admin(self):
        self.force_login_user(self._get_admin(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_manager(self):
        self.force_login_user(self._get_manager(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_client(self):
        self.force_login_user(self._get_client(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_consultant(self):
        self.force_login_user(self._get_consultant(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/')

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/asset-handover-document-media/', {'all': True})

        self.assertUnauthorized(response)

    def retrieve_filters(self):
        return (
            (
                '/asset_handover_document_media/retrieve_by_company_admin.json',
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                '/asset_handover_document_media/retrieve_by_project_admin.json',
                {'groups': User.Group.ADMIN.value, 'project': 5},
            ),
            (
                '/asset_handover_document_media/retrieve_by_project_manager.json',
                {'groups': User.Group.MANAGER.value, 'project': 5},
            ),
            (
                '/asset_handover_document_media/retrieve_by_project_client.json',
                {'groups': User.Group.CLIENT.value, 'project': 5},
            ),
            (
                '/asset_handover_document_media/retrieve_by_project_subcontractor.json',
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5, 'company': 1},
            ),
            (
                '/asset_handover_document_media/retrieve_by_project_consultant.json',
                {'groups': User.Group.CONSULTANT.value, 'project': 5},
            ),
        )

    @data_provider(retrieve_filters)
    def test_retrieve(self, fixture, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/9/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_retrieve_by_non_project_admin(self):
        self.force_login_user(self._get_admin(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_manager(self):
        self.force_login_user(self._get_manager(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_client(self):
        self.force_login_user(self._get_client(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_consultant(self):
        self.force_login_user(self._get_consultant(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/')

        self.assertUnauthorized(response)

    def test_create_by_superuser(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/'
                                                  'create_asset_handover_document_media.json')
        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {'asset_handover_document': 5, 'media': 2, 'uid': creation_data['uid']})
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, {
            'asset_handover_document_media__asset_handover_document': 5,
            'asset_handover_document_media__media': 2,
            'comment': None,
            'user': superuser.pk
        })

    def test_create_by_project_subcontractor(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media_by_subcontractor.json')
        self.force_login_user(self._get_subcontractor(project=5, company=1).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {'asset_handover_document': 1, 'media': 8})

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'troom.png')
    def test_bulk_create_by_superuser(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_superuser().pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertCreated(response)

        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media/bulk_create_by_superuser.json')
        # Make sure that documents saved with requested media copy.
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=1)])
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=2)])

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'troom.png')
    def test_bulk_create_by_company_admin(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        creation_data = self.load_request_fixture('/asset_handover_document_media/'
                                                  'bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertCreated(response)
        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media/bulk_create_by_company_admin.json')
        # Make sure that documents saved with requested media copy.
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=1)])
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=2)])

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'troom.png')
    def test_bulk_create_by_project_admin(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        creation_data = self.load_request_fixture('/asset_handover_document_media/'
                                                  'bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_admin(project=5).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertCreated(response)

        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media/bulk_create_by_project_admin.json')
        # Make sure that documents saved with requested media copy.
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=1)])
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=2)])

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'troom.png')
    def test_bulk_create_by_project_manager(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        creation_data = self.load_request_fixture('/asset_handover_document_media/'
                                                  'bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_manager(project=5).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertCreated(response)

        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media/bulk_create_by_project_manager.json')
        # Make sure that documents saved with requested media copy.
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=1)])
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=2)])

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'troom.png')
    def test_bulk_create_by_project_subcontractor(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_subcontractor(project=5).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertCreated(response)

        self._remove_media_fields_with_hash(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media/bulk_create_by_project_subcontractor.json')
        # Make sure that documents saved with requested media copy.
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=1)])
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {
                                   'asset_handover_document__asset_handover__package_activity': 7,
                                   'asset_handover_document__document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
                                   'media__name__contains': 'troom'
                               },
                               [~Q(media=2)])

    def test_forbid_bulk_create_by_non_project_admin(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_admin(~Q(project=5)).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_non_project_manager(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_manager(~Q(project=5)).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_non_project_subcontractor(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertForbidden(response)

    def test_unauthorized_bulk_create(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/bulk_create_asset_handover_documents.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertUnauthorized(response)

    def test_bulk_create_with_all_invalid_package_activities_for_subcontractor(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/'
                                                  'bulk_create_with_all_invalid_package_activities.json')
        self.force_login_user(self._get_subcontractor(project=5).pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/bulk/', creation_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You\'re not allowed to create media."]}')

    def test_forbid_create_by_project_admin(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')
        user = self._get_admin(project=5)
        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {'asset_handover_document': 5, 'media': 2})

    def test_forbid_create_by_project_manager(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')
        user = self._get_manager(project=5)

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {'asset_handover_document': 5, 'media': 2})

    def test_forbid_create_by_project_client(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')
        user = self._get_client(project=5)

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_consultant(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')
        user = self._get_consultant(~Q(project=5))

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_subcontractor(self):
        user = self._get_subcontractor(~Q(project=5))
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media/create_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        self.force_login_user(self._get_superuser().pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocumentMedia, 1)

    def test_delete_by_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(project=5, company=1).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocumentMedia, 1)

    def test_delete_by_project_consultant(self):
        self.force_login_user(self._get_consultant(project=5).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_delete_by_project_admin(self):
        self.force_login_user(self._get_admin(project=5).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocumentMedia, 1)

    def test_delete_by_project_manager(self):
        self.force_login_user(self._get_manager(project=5).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocumentMedia, 1)

    def test_forbid_delete_by_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(project=5, company=4).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/7/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_consultant(self):
        self.force_login_user(self._get_consultant(~Q(project=5)).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_forbid_delete_by_project_client(self):
        self.force_login_user(self._get_client(project=5).pk)
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/asset-handover-document-media/1/')

        self.assertUnauthorized(response)

    def download_filters(self):
        return (
            (
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                {'groups': User.Group.ADMIN.value, 'project': 8},
            ),
            (
                {'groups': User.Group.MANAGER.value, 'project': 8},
            ),
            (
                {'groups': User.Group.CLIENT.value, 'project': 8},
            ),
            (
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 8},
            ),
            (
                {'groups': User.Group.CONSULTANT.value, 'project': 8},
            ),
        )

    @data_provider(download_filters)
    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_download(self, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/8/asset-handover-document-media/11/download/')

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    def test_forbid_download_in_not_allowed_status_by_project_client(self):
        project_client = self._get_client(project=8)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/8/asset-handover-document-media/12/download/')

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_information_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/asset-handovers/information-csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/asset_handover_document_media/handover_information_csv_report_created.html'
            }
        ])

    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch.object(HandoverDocumentMediaDownloadService, '_HandoverDocumentMediaDownloadService__generate_archive_name', mock_generated_archive_name)
    def test_get_archive_by_superuser(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        data = {'asset_handover_document_media': [1, 2]}
        url = reverse('asset_handover_document_media_batch', kwargs={'project_pk': 5})

        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.post(url, data)

        self.assertOk(response)
        self.assertDatabaseHas(Media, {'name': 'archive.zip'})

        with ZipFile('media/archive.zip', 'r') as zip_archive:
            media_names = list(
                Media.objects.filter(
                    assethandoverdocumentmedia__id__in=data['asset_handover_document_media']
                ).values_list('name', flat=True)
            )
            files_namelist = zip_archive.namelist()
            for media_name in media_names:
                self.assertIn(media_name, files_namelist)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report - Archive of selected files',
                'to': [superuser.email],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/asset_handover_document_media/'
                                                         + 'notify_about_ability_to_download_archive.html'
            }
        ])
