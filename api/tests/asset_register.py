from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from freezegun import freeze_time
from rest_framework.reverse import reverse

from api.models import AssetHandoverDocument, User, AssetHandoverInformation, AssetRegister
from api.models.asset_handover import AssetHandover
from api.tests.test import TestCase, data_provider


class AssetRegisterTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/asset_register.json',
    ]

    WORKING_PROJECT = 5
    PROJECT_FOR_CREATION = 6

    def test_create_by_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_company_admin(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetRegister, data)

    def test_create_by_non_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_company_admin(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_admin(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_non_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_admin(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_manager(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_non_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_manager(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_client(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_non_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_client(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_consultant(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_non_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_consultant(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_subcontractor(project=self.PROJECT_FOR_CREATION)
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_create_by_non_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.PROJECT_FOR_CREATION})
        data = self.load_request_fixture('/asset_register/create_asset_register.json')
        self._log_in_as_subcontractor(~Q(project=self.PROJECT_FOR_CREATION))
        response = self.client.post(path, data)

        self.assertForbidden(response)

    def test_retrieve_by_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_register/retrieve.json')

    def test_retrieve_by_non_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_retrieve_by_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)

    def test_retrieve_by_non_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_retrieve_by_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)

    def test_retrieve_by_non_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_retrieve_by_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)

    def test_retrieve_by_non_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_retrieve_by_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)

    def test_retrieve_by_non_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_retrieve_by_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(path)

        self.assertOk(response)

    def test_retrieve_by_non_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(path)

        self.assertForbidden(response)

    def test_delete_by_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertNoContent(response)
        self.assertSoftDeleted(AssetRegister, {'project': self.WORKING_PROJECT})

    def test_delete_by_non_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_non_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_non_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_non_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_non_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_delete_by_non_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(path)

        self.assertForbidden(response)

    def test_update_by_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_company_admin(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertOk(response)
        self.assertDatabaseHas(AssetRegister, {'project': self.WORKING_PROJECT, **data})

    def test_update_by_non_project_company_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_company_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_non_project_admin(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_non_project_manager(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_non_project_client(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_non_project_consultant(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.put(path, data)

        self.assertForbidden(response)

    def test_update_by_non_project_subcontractor(self):
        path = reverse('asset_register-list', kwargs={'project_pk': self.WORKING_PROJECT})
        data = self.load_request_fixture('/asset_register/update_asset_register.json')

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(path)

        self.assertForbidden(response)
