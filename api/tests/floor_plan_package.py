from django.db.models import Q
from django.urls import reverse

from api.tests.test import TestCase, data_provider


class FloorPlanPackageTest(TestCase):
    WORKING_PROJECT = 5
    fixtures = [
        'api/tests/fixtures/dumps/floor_plan_package.json',
    ]

    def get_filters(self):
        return (
            (
                {'all': True, 'building': 'building1', 'level': 'level1'},
                '/floor_plan_package/list_all_floor_plan.json',
            ),
        )

    @data_provider(get_filters)
    def test_search_by_company_admin(self, filters, fixture):
        self._log_in_as_company_admin()
        response = self.client.get(reverse('floor_plan_package_list', kwargs={'project_pk': self.WORKING_PROJECT}), filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_admin(self):
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(reverse('floor_plan_package_list', kwargs={'project_pk': self.WORKING_PROJECT}))

        self.assertForbidden(response)

    def test_forbid_search_by_non_client(self):
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(reverse('floor_plan_package_list', kwargs={'project_pk': self.WORKING_PROJECT}))

        self.assertForbidden(response)

    def test_forbid_search_by_non_consultant(self):
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(reverse('floor_plan_package_list', kwargs={'project_pk': self.WORKING_PROJECT}))

        self.assertForbidden(response)

    def test_forbid_search_by_non_subcontractor(self):
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(reverse('floor_plan_package_list', kwargs={'project_pk': self.WORKING_PROJECT}))

        self.assertForbidden(response)
