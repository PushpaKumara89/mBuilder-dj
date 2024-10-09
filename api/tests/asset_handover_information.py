from django.core.files.storage import FileSystemStorage
from django.db.models import Q

from api.models import AssetHandoverInformation
from api.tests.test import TestCase


class AssetHandoverInformationTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/asset_handover_information.json',
    ]
    fss = FileSystemStorage()

    def test_create_by_superuser(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_superuser().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverInformation, creation_data)

    def test_create_by_company_admin(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverInformation, creation_data)

    def test_create_by_admin(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_admin().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverInformation, creation_data)

    def test_create_by_manager(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_manager().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverInformation, creation_data)

    def test_forbid_create_by_client(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_client().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_consultant(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_consultant().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_subcontractor(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        self.force_login_user(self._get_subcontractor().pk)
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        creation_data = self.load_request_fixture('/asset_handover_information/create_asset_handover_information.json')
        response = self.client.post('/api/projects/5/asset-handover-information/', creation_data)

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_superuser().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetHandoverInformation, {'pk': 1, **update_data})

    def test_update_by_company_admin(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetHandoverInformation, {'pk': 1, **update_data})

    def test_update_by_admin(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_admin().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetHandoverInformation, {'pk': 1, **update_data})

    def test_update_by_manager(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_manager().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetHandoverInformation, {'pk': 1, **update_data})

    def test_forbid_update_by_client(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_client().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_consultant(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_consultant().pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_subcontractor(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        self.force_login_user(self._get_subcontractor(~Q(project=5)).pk)
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_data = self.load_request_fixture('/asset_handover_information/update_asset_handover_information.json')
        response = self.client.put('/api/projects/5/asset-handover-information/1/', update_data)

        self.assertUnauthorized(response)

    def test_retrieve_by_superuser(self):
        self.force_login_user(self._get_superuser().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_information/get_by_superuser.json')

    def test_retrieve_by_company_admin(self):
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_information/get_by_company_admin.json')

    def test_retrieve_by_admin(self):
        self.force_login_user(self._get_admin().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_information/get_by_admin.json')

    def test_retrieve_by_manager(self):
        self.force_login_user(self._get_manager().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_information/get_by_manager.json')

    def test_forbid_retrieve_by_client(self):
        self.force_login_user(self._get_client().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertForbidden(response)

    def test_retrieve_by_consultant(self):
        self.force_login_user(self._get_consultant().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertForbidden(response)

    def test_retrieve_by_subcontractor(self):
        self.force_login_user(self._get_subcontractor().pk)
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertForbidden(response)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/5/asset-handover-information/1/')

        self.assertUnauthorized(response)
