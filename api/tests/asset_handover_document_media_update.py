from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import User, AssetHandoverDocumentMediaUpdate, AssetHandoverDocumentMedia
from api.tests.test import TestCase, data_provider


class AssetHandoverDocumentMediaUpdateTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/asset_handover_document_media_update.json']

    WORKING_PROJECT = 5

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'id', 'expand': [
                    'expanded_asset_handover_document_media.expanded_upload_update.expanded_user',
                    'expanded_asset_handover_document_media.expanded_upload_update.expanded_user.expanded_user_company',
                ]},
                '/asset_handover_document_media_update/get_all_by_company_admin.json',
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_document_media_update/get_all_by_project_admin.json',
                {'groups': User.Group.ADMIN.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_document_media_update/get_all_by_project_manager.json',
                {'groups': User.Group.MANAGER.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_document_media_update/get_all_by_project_client.json',
                {'groups': User.Group.CLIENT.value, 'project': 5},
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_document_media_update/get_all_by_project_subcontractor.json',
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5, 'company': 1},
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_document_media_update/get_all_by_project_consultant.json',
                {'groups': User.Group.CONSULTANT.value, 'project': 5},
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_admin(self):
        self.force_login_user(self._get_admin(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_manager(self):
        self.force_login_user(self._get_manager(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_client(self):
        self.force_login_user(self._get_client(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_consultant(self):
        self.force_login_user(self._get_consultant(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/')

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/', {'all': True})

        self.assertUnauthorized(response)

    def test_bulk_create_by_project_client(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/bulk_create_by_client.json')
        project_client = self._get_client(project=self.WORKING_PROJECT)
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })

        self.force_login_user(project_client.pk)
        response = self.client.post(url, creation_data)

        self.assertCreated(response)

        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'asset_handover_document': updating_asset_handover_document,
            'assethandoverdocumentmediaupdate__old_data__status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
            'assethandoverdocumentmediaupdate__new_data__status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })

    def test_bulk_create_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=self.WORKING_PROJECT, id=8)
        updating_asset_handover_document = 1
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/bulk_create_by_subcontractor.json')
        self.force_login_user(project_subcontractor.pk)
        response = self.client.post(url, creation_data)

        self.assertCreated(response)

        self.assertSoftDeleted(AssetHandoverDocumentMedia, {
            'asset_handover_document': updating_asset_handover_document,
            'assethandoverdocumentmediaupdate__old_data__status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
            'assethandoverdocumentmediaupdate__new_data__status': AssetHandoverDocumentMedia.Status.REMOVED,
        })

    def test_bulk_create_by_multiplex(self):
        project_multiplex = self._get_staff(project=self.WORKING_PROJECT)
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/bulk_create_by_multiplex.json')
        self.force_login_user(project_multiplex.pk)
        response = self.client.post(url, creation_data)

        self.assertCreated(response)

        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'asset_handover_document': updating_asset_handover_document,
            'assethandoverdocumentmediaupdate__old_data__status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
            'assethandoverdocumentmediaupdate__new_data__status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })

    def test_bulk_create_invalid_transition_by_client(self):
        updating_asset_handover_document = 1
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_invalid_transition_by_client.json')
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url, creation_data)

        self.assertBadRequest(response)

        # Check all document media changed status to the same.
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_invalid_transition_by_subcontractor(self):
        updating_asset_handover_document = 1
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_invalid_transition_by_subcontractor.json')
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT, id=8)
        response = self.client.post(url, creation_data)

        self.assertBadRequest(response)

        # Check all document media changed status to the same.
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_invalid_transition_by_multiplex(self):
        updating_asset_handover_document = 1
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_invalid_transition_by_multiplex.json')
        self._log_in_as_staff(project=self.WORKING_PROJECT)
        response = self.client.post(url, creation_data)

        self.assertBadRequest(response)

        # Check all document media changed status to the same.
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_forbid_bulk_create_by_admin(self):
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, creation_data)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_manager(self):
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, creation_data)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_client(self):
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, creation_data)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_subcontractor(self):
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_subcontractor(~Q(id=8), project=self.WORKING_PROJECT)
        response = self.client.post(url, creation_data)

        self.assertForbidden(response)

    def test_create_by_superuser(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')
        self.force_login_user(self._get_superuser().pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, creation_data['new_data'])
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, creation_data)

    def test_forbid_create_by_non_project_consultant(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')
        user = self._get_consultant(~Q(project=5))

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_subcontractor(self):
        user = self._get_subcontractor(~Q(project=5))
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_client(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')
        user = self._get_consultant(~Q(project=5))

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_admin(self):
        user = self._get_admin(~Q(project=5))
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_manager(self):
        user = self._get_manager(~Q(project=5))
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')

        self.force_login_user(user.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_update/'
                                                  'create_asset_handover_document_media_update.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/1/updates/', creation_data)

        self.assertUnauthorized(response)

    def get_retrieve_filters(self):
        return (
            (
                {'groups': User.Group.COMPANY_ADMIN.value},
            ),
            (
                {'groups': User.Group.ADMIN.value, 'project': 5},
            ),
            (
                {'groups': User.Group.MANAGER.value, 'project': 5},
            ),
            (
                {'groups': User.Group.CLIENT.value, 'project': 5},
            ),
            (
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5, 'company': 1},
            ),
            (
                {'groups': User.Group.CONSULTANT.value, 'project': 5},
            ),
        )

    @data_provider(get_retrieve_filters)
    def test_retrieve(self, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_document_media_update/'
                                                'retrieve_asset_handover_document_media_update.json')

    def test_forbid_retrieve_by_non_project_admin(self):
        self.force_login_user(self._get_admin(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_manager(self):
        self.force_login_user(self._get_manager(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_client(self):
        self.force_login_user(self._get_client(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_subcontractor(self):
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_consultant(self):
        self.force_login_user(self._get_consultant(~Q(project=5)).pk)
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/5/asset-handover-document-media/1/updates/1/')

        self.assertUnauthorized(response)
