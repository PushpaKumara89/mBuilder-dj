from django.db.models import Q

from api.models import ApiKey, User
from api.tests.test import TestCase, data_provider


class ApiKeyTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/api_key.json',
    ]

    def test_create_key(self):
        request_data = self.load_request_fixture('/api_keys/create_api_key.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/api-keys/', request_data)

        self.assertCreated(response)
        self.assertDatabaseHas(ApiKey, request_data)

    def test_create_key_with_company_not_related_to_project_users(self):
        request_data = self.load_request_fixture('/api_keys/create_api_key_with_invalid_company.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/api-keys/', request_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["Users from this company don\'t exists in the project."]}')

    def test_forbid_create_for_non_company_admin(self):
        request_data = self.load_request_fixture('/api_keys/create_api_key.json')

        self._log_in_as_user(~Q(group=User.Group.COMPANY_ADMIN.value), is_superuser=False)
        response = self.client.post('/api/api-keys/', request_data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        request_data = self.load_request_fixture('/api_keys/create_api_key.json')

        response = self.client.post('/api/api-keys/', request_data)

        self.assertUnauthorized(response)

    def test_update(self):
        request_data = self.load_request_fixture('/api_keys/update_api_key.json')

        self._log_in_as_superuser()
        response = self.client.put('/api/api-keys/1/', request_data)

        self.assertOk(response)
        self.assertDatabaseHas(ApiKey, request_data)

    def test_forbid_update_for_non_company_admin(self):
        request_data = self.load_request_fixture('/api_keys/update_api_key.json')

        self._log_in_as_user(~Q(group=User.Group.COMPANY_ADMIN.value), is_superuser=False)
        response = self.client.put('/api/api-keys/1/', request_data)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        request_data = self.load_request_fixture('/api_keys/update_api_key.json')
        response = self.client.put('/api/api-keys/1/', request_data)

        self.assertUnauthorized(response)

    def test_delete(self):
        self._log_in_as_superuser()
        response = self.client.delete('/api/api-keys/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(ApiKey, 1)

    def test_delete_by_non_company_admin(self):
        self._log_in_as_user(~Q(group=User.Group.COMPANY_ADMIN.value), is_superuser=False)
        response = self.client.delete('/api/api-keys/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/api-keys/1/')

        self.assertUnauthorized(response)

    def get_filters_for_search(self):
        return (
            (
                {'project': [1]},
                '/api_keys/filter_by_project.json'
            ),
            (
                {'company': [2]},
                '/api_keys/filter_by_company.json'
            ),
            (
                {'expires_at': '2020-08-30'},
                '/api_keys/filter_by_expires_at.json'
            ),
            (
                {'expires_at__lt': '2020-09-30'},
                '/api_keys/filter_by_expires_at_less.json'
            ),
            (
                {'expires_at__gt': '2020-09-30'},
                '/api_keys/filter_by_expires_at_greater.json'
            ),
            (
                {'search': 'tower'},
                '/api_keys/search_by_project_name.json'
            ),
            (
                {'search': 'demo'},
                '/api_keys/search_by_project_number.json'
            ),
            (
                {'search': '0a13'},
                '/api_keys/search_by_project_token.json'
            ),
            (
                {'search': 'Ford'},
                '/api_keys/search_by_company_name.json'
            ),
            (
                {'expand': ['expanded_project', 'expanded_company']},
                '/api_keys/list_with_expanded.json'
            ),
        )

    @data_provider(get_filters_for_search)
    def test_search(self, filters: dict, fixture: str):
        self._log_in_as_superuser()
        response = self.client.get('/api/api-keys/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_company_admin(self):
        self._log_in_as_user(~Q(group=User.Group.COMPANY_ADMIN.value), is_superuser=False)
        response = self.client.get('/api/api-keys/')

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/api-keys/')

        self.assertUnauthorized(response)
