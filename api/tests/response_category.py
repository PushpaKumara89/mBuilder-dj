from django.db.models import Q

from api.models import ResponseCategory, User
from api.tests.test import TestCase, data_provider


class ResponseCategoryTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/response_category.json']

    def test_create(self):
        company_admin = self._get_company_admin()
        new_response_category = self.load_request_fixture('/response_category/new_response_category.json')

        self.force_login_user(company_admin.pk)
        response = self.client.post('/api/projects/1/response-categories/', new_response_category)

        self.assertCreated(response)
        self.assertDatabaseHas(ResponseCategory, new_response_category)
        self.assertEventsExist('/response_category/create_response_category_events_assertion.json')

    def test_forbid_create(self):
        non_company_admin = self._get_user(~Q(groups=User.Group.COMPANY_ADMIN.value) & ~Q(is_superuser=True))
        new_response_category = self.load_request_fixture('/response_category/new_response_category.json')

        self.force_login_user(non_company_admin.pk)
        response = self.client.post('/api/projects/1/response-categories/', new_response_category)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_response_category = self.load_request_fixture('/response_category/new_response_category.json')
        response = self.client.post('/api/projects/1/response-categories/', new_response_category)

        self.assertUnauthorized(response)

    def test_update(self):
        company_admin = self._get_company_admin()
        update_response_category = self.load_request_fixture('/response_category/update_response_category.json')

        self.force_login_user(company_admin.pk)
        response = self.client.put('/api/projects/1/response-categories/1/', update_response_category)

        self.assertOk(response)
        self.assertDatabaseHas(ResponseCategory, {'pk': 1, **update_response_category})
        self.assertEventsExist('/response_category/update_response_category_events_assertion.json')

    def test_forbid_update(self):
        non_company_admin = self._get_user(~Q(groups=User.Group.COMPANY_ADMIN.value) & ~Q(is_superuser=True))
        update_response_category = self.load_request_fixture('/response_category/update_response_category.json')

        self.force_login_user(non_company_admin.pk)
        response = self.client.put('/api/projects/1/response-categories/1/', update_response_category)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_response_category = self.load_request_fixture('/response_category/update_response_category.json')

        response = self.client.put('/api/projects/1/response-categories/1/', update_response_category)

        self.assertUnauthorized(response)

    def test_delete(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.delete('/api/projects/1/response-categories/2/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(ResponseCategory, 2)
        self.assertEventsExist('/response_category/delete_response_category_events_assertion.json')

    def test_forbid_delete(self):
        non_company_admin = self._get_user(~Q(groups=User.Group.COMPANY_ADMIN.value) & ~Q(is_superuser=True))
        self.force_login_user(non_company_admin.pk)
        response = self.client.delete('/api/projects/1/response-categories/2/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/1/response-categories/2/')

        self.assertUnauthorized(response)

    def test_get(self):
        project_user = self._get_user(project=1)
        self.force_login_user(project_user.pk)
        response = self.client.get('/api/projects/1/response-categories/3/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/response_category/get_response_category.json')

    def test_forbid_get(self):
        non_project_user = self._get_user(~Q(project=1) & ~Q(groups=User.Group.COMPANY_ADMIN.value) & ~Q(is_superuser=True))
        self.force_login_user(non_project_user.pk)
        response = self.client.get('/api/projects/1/response-categories/3/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/1/response-categories/3/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': '-name'},
                '/response_category/get_all_desc_order.json',
            ),
            (
                {'page': 2, 'per_page': 2},
                '/response_category/get_page_per_page.json',
            ),
            (
                {'search': 'one'},
                '/response_category/search.json',
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture):
        project_user = self._get_user(project=1)
        self.force_login_user(project_user.pk)
        response = self.client.get('/api/projects/1/response-categories/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)
