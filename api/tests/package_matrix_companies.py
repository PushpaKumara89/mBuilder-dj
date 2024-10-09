from django.db.models import Q

from api.models import PackageMatrixCompany
from api.tests.test import TestCase, data_provider


class PackageMatrixCompaniesTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_matrix_companies.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser(editmode__project=4)
        new_package_matrix_company = self.load_request_fixture(
            '/package_matrix_companies/create_package_matrix_companies.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/4/package-matrix-companies/', new_package_matrix_company)

        self.assertCreated(response)
        # todo Rework creating multiple media with unique hash
        # self.assertEventsExist('/package_matrix_companies/create_package_matrix_company_assertion.json')

    def test_create_by_project_staff_in_edit_mode(self):
        project_staff = self._get_staff(project=4, editmode__project=4)
        new_package_matrix_company = self.load_request_fixture(
            '/package_matrix_companies/create_package_matrix_companies.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/4/package-matrix-companies/', new_package_matrix_company)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageMatrixCompany, {'company': 2, 'package_matrix': 6})
        self.assertDatabaseHas(PackageMatrixCompany, {'company': 3, 'package_matrix': 6})

    def test_forbid_create_not_in_edit_mode(self):
        staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=4))
        new_package_matrix_company = self.load_request_fixture(
            '/package_matrix_companies/create_package_matrix_companies.json')

        self.force_login_user(staff_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/4/package-matrix-companies/', new_package_matrix_company)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_matrix_company = self.load_request_fixture(
            '/package_matrix_companies/create_package_matrix_companies.json')
        response = self.client.post('/api/projects/4/package-matrix-companies/', new_package_matrix_company)

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/package-matrix-companies/1/')

        self.assertNoContent(response)
        self.assertHardDeleted(PackageMatrixCompany, 1)
        # todo Rework creating multiple media with unique hash
        # self.assertEventsExist('/package_matrix_companies/delete_package_matrix_company_assertion.json')

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project=5, editmode__project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/package-matrix-companies/1/')

        self.assertNoContent(response)
        self.assertHardDeleted(PackageMatrixCompany, 1)

    def test_forbid_delete_not_in_edit_mode(self):
        staff = self._get_user(~Q(editmode__project=5), project=5)
        self.force_login_user(staff.pk)
        response = self.client.delete('/api/projects/5/package-matrix-companies/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/package-matrix-companies/1/')

        self.assertUnauthorized(response)

    def get_filters_for_list(self):
        return (
            (
                {'package_matrix': 5},
                '/package_matrix_companies/get_all_by_package_matrix.json',
            ),
            (
                {'company': 2},
                '/package_matrix_companies/get_all_by_company.json',
            ),
        )

    @data_provider(get_filters_for_list)
    def test_list_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-matrix-companies/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_list)
    def test_list_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-matrix-companies/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_list_by_staff_from_another_project(self):
        staff = self._get_staff(~Q(project=5))
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-matrix-companies/')

        self.assertForbidden(response)

    def test_unauthorized_list(self):
        response = self.client.get('/api/projects/5/package-matrix-companies/')

        self.assertUnauthorized(response)
