from api.models import PackageHandoverDocumentGroup
from api.tests.test import TestCase, data_provider


class PackageHandoverDocumentGroupTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/package_handovers.json',
        'api/tests/fixtures/dumps/package_handover_document.json'
    ]

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/create_package_handover_document_group.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/package-handover-document-groups/', new_package_handover_document_group)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentGroup, new_package_handover_document_group)

    def test_forbid_create(self):
        non_superuser = self._get_user(is_superuser=False)
        new_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/create_package_handover_document_group.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/package-handover-document-groups/', new_package_handover_document_group)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/create_package_handover_document_group.json')
        response = self.client.post('/api/package-handover-document-groups/', new_package_handover_document_group)

        self.assertUnauthorized(response)

    def test_update(self):
        superuser = self._get_superuser()
        update_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/update_package_handover_document_group.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/package-handover-document-groups/2/', update_package_handover_document_group)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandoverDocumentGroup, {'pk': 2, **update_package_handover_document_group})

    def test_forbid_update(self):
        update_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/update_package_handover_document_group.json')
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/package-handover-document-groups/1/', update_package_handover_document_group)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package_handover_document_group = self.load_request_fixture('/package_handover_document_group/update_package_handover_document_group.json')
        response = self.client.put('/api/package-handover-document-groups/1/', update_package_handover_document_group)

        self.assertUnauthorized(response)

    def test_delete(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/package-handover-document-groups/2/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(PackageHandoverDocumentGroup, 2)

    def test_forbid_delete(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/package-handover-document-groups/3/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/package-handover-document-groups/3/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/package-handover-document-groups/2/', {'expand': ['expanded_users_count']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_group/get_package_handover_document_group.json')

    def test_forbid_get(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/package-handover-document-groups/2/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/package-handover-document-groups/2/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'name': 'Subcontractor Documents', 'sort': '-name'},
                '/package_handover_document_group/get_all_desc_order.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_handover_document_group/get_page_per_page.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'search': 'sub'},
                '/package_handover_document_group/search.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'package': [4], 'sort': 'name'},
                '/package_handover_document_group/filter_by_package.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'package_activity': [2], 'sort': 'name'},
                '/package_handover_document_group/filter_by_package_activity.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'package': [4], 'sort': 'name'},
                '/package_handover_document_group/filter_by_package_by_consultant.json',
                {'user_pk': self._get_consultant(project=5).pk}
            ),
            (
                {'package_activity': [2], 'sort': 'name'},
                '/package_handover_document_group/filter_by_package_activity_by_subcontractor.json',
                {'user_pk': self._get_subcontractor(project=5).pk}
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture, params):
        self.force_login_user(params['user_pk'])
        response = self.client.get('/api/package-handover-document-groups/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_search(self):
        response = self.client.get('/api/package-handover-document-groups/', {'search': 'sub'})

        self.assertUnauthorized(response)
