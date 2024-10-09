from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import FloorPlanArea
from api.tests.test import TestCase, data_provider


class FloorPlanAreaTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/floor_plan_area.json',
    ]

    WORKING_PROJECT = 5

    def test_create_by_superuser(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.post(url, data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/create_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, data)

    def test_create_by_company_admin(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin()
        response = self.client.post(url, data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/create_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, data)

    def test_create_by_project_admin(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/create_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, data)

    def test_create_by_project_manager(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/create_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, data)

    def test_create_by_project_subcontractor(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_project_client(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_project_consultant(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_non_project_admin(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_non_project_manager(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_non_project_subcontractor(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_non_project_client(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_create_by_non_project_consultant(self):
        data = self.load_request_fixture('/floor_plan_area/create_floor_plan_area.json')
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_update_by_superuser(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_superuser()
        response = self.client.put(url, data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/update_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, {'pk': updating_floor_plan_area} | data)

    def test_update_by_company_admin(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_company_admin()
        response = self.client.put(url, data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/update_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, {'pk': updating_floor_plan_area} | data)

    def test_update_by_project_admin(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.put(url, data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/update_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, {'pk': updating_floor_plan_area} | data)

    def test_update_by_project_manager(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.put(url, data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/update_floor_plan_area_assertion.json')

        self.assertDatabaseHas(FloorPlanArea, {'pk': updating_floor_plan_area} | data)

    def test_update_by_project_subcontractor(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_project_client(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_project_consultant(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_non_project_admin(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_non_project_manager(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_non_project_subcontractor(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_non_project_client(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_update_by_non_project_consultant(self):
        updating_floor_plan_area = 1
        data = self.load_request_fixture('/floor_plan_area/update_floor_plan_area.json')
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan_area
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.put(url, data)

        self.assertForbidden(response)

    def test_delete_by_superuser(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_superuser()
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlanArea, deleting_floor_plan_area)

    def test_delete_by_company_admin(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_company_admin()
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlanArea, deleting_floor_plan_area)

    def test_delete_by_project_admin(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlanArea, deleting_floor_plan_area)

    def test_delete_by_project_manager(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlanArea, deleting_floor_plan_area)

    def test_delete_by_project_subcontractor(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_project_client(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_project_consultant(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_non_project_admin(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_non_project_manager(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_non_project_subcontractor(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_non_project_client(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_delete_by_non_project_consultant(self):
        deleting_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.delete(url)

        self.assertForbidden(response)

    def test_retrieve_by_superuser(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/retrieve_floor_plan_area.json')

    def test_retrieve_by_company_admin(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_company_admin()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/retrieve_floor_plan_area.json')

    def test_retrieve_by_project_admin(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/retrieve_floor_plan_area.json')

    def test_retrieve_by_project_manager(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area/retrieve_floor_plan_area.json')

    def test_retrieve_by_project_subcontractor(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_project_client(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_project_consultant(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_admin(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_manager(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_subcontractor(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_client(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_consultant(self):
        retrieving_floor_plan_area = 1
        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': retrieving_floor_plan_area
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def get_filters_for_search(self):
        return (
            (
                {'sort': 'area', 'floor_plan': [1, 2]},
                '/floor_plan_area/get_filtered_by_plan.json'
            ),
            (
                {'sort': 'area', 'all': True},
                '/floor_plan_area/get_all.json'
            ),
            (
                {'sort': 'area', 'all': True, 'package': [4]},
                '/floor_plan_area/get_filtered_by_package.json'
            ),
            (
                {'sort': 'area', 'all': True, 'building': ['building1']},
                '/floor_plan_area/get_filtered_by_building.json'
            ),
            (
                {'sort': 'area', 'all': True, 'level': ['level1']},
                '/floor_plan_area/get_filtered_by_level.json'
            ),
            (
                {'sort': 'area', 'all': True, 'area': ['beatle']},
                '/floor_plan_area/get_filtered_by_area.json'
            ),
        )

    @data_provider(get_filters_for_search)
    def test_list_by_superuser(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_company_admin(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_project_admin(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_project_manager(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_project_subcontractor(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_project_client(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search)
    def test_list_by_project_consultant(self, filters, fixture):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_by_non_project_admin(self):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_manager(self):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_subcontractor(self):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_client(self):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_consultant(self):
        url = reverse('floor_plan_area_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_bulk_actions_by_superuser(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_superuser()
        response = self.client.post(url, data)

        self.assertNoContent(response)

        for creation_data in data['create']:
            self.assertDatabaseHas(FloorPlanArea, creation_data)

        for update_data in data['update']:
            self.assertDatabaseHas(FloorPlanArea, update_data)

        for deletion_data in data['delete']:
            self.assertDatabaseMissing(FloorPlanArea, deletion_data)

    def test_bulk_actions_by_company_admin(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_company_admin()
        response = self.client.post(url, data)

        self.assertNoContent(response)

        for creation_data in data['create']:
            self.assertDatabaseHas(FloorPlanArea, creation_data)

        for update_data in data['update']:
            self.assertDatabaseHas(FloorPlanArea, update_data)

        for deletion_data in data['delete']:
            self.assertDatabaseMissing(FloorPlanArea, deletion_data)

    def test_bulk_actions_by_project_admin(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertNoContent(response)

        for creation_data in data['create']:
            self.assertDatabaseHas(FloorPlanArea, creation_data)

        for update_data in data['update']:
            self.assertDatabaseHas(FloorPlanArea, update_data)

        for deletion_data in data['delete']:
            self.assertDatabaseMissing(FloorPlanArea, deletion_data)

    def test_bulk_actions_by_project_manager(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertNoContent(response)

        for creation_data in data['create']:
            self.assertDatabaseHas(FloorPlanArea, creation_data)

        for update_data in data['update']:
            self.assertDatabaseHas(FloorPlanArea, update_data)

        for deletion_data in data['delete']:
            self.assertDatabaseMissing(FloorPlanArea, deletion_data)

    def test_bulk_actions_by_project_subcontractor(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_project_client(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_project_consultant(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_non_project_admin(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_non_project_manager(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_non_project_subcontractor(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_non_project_client(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)

    def test_bulk_actions_by_non_project_consultant(self):
        data = self.load_request_fixture('/floor_plan_area/bulk_actions.json')
        url = reverse('floor_plan_area_bulk', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, data)

        self.assertForbidden(response)
