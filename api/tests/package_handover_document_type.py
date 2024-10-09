from api.models import PackageHandoverDocumentType
from api.tests.test import TestCase, data_provider


class PackageHandoverDocumentTypeTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_handover_document_types.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/create_package_handover_document_type.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/package-handover-document-types/', new_package_handover_document_type)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentType, new_package_handover_document_type)

    def test_forbid_create(self):
        non_superuser = self._get_user(is_superuser=False)
        new_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/create_package_handover_document_type.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/package-handover-document-types/', new_package_handover_document_type)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/create_package_handover_document_type.json')
        response = self.client.post('/api/package-handover-document-types/', new_package_handover_document_type)

        self.assertUnauthorized(response)

    def test_update(self):
        superuser = self._get_superuser()
        update_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/update_package_handover_document_type.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/package-handover-document-types/2/', update_package_handover_document_type)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandoverDocumentType, {'pk': 2, **update_package_handover_document_type})

    def test_forbid_update(self):
        update_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/update_package_handover_document_type.json')
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/package-handover-document-types/1/', update_package_handover_document_type)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package_handover_document_type = self.load_request_fixture('/package_handover_document_type/update_package_handover_document_type.json')
        response = self.client.put('/api/package-handover-document-types/1/', update_package_handover_document_type)

        self.assertUnauthorized(response)

    def test_delete(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/package-handover-document-types/2/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(PackageHandoverDocumentType, 2)

    def test_forbid_delete(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/package-handover-document-types/3/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/package-handover-document-types/3/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/package-handover-document-types/2/', {'expand': ['expanded_group']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_package_handover_document_type.json')

    def test_get_by_staff(self):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/package-handover-document-types/2/', {'expand': ['expanded_group']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_package_handover_document_type.json')

    def test_forbid_get(self):
        user = self._get_user(is_superuser=False, is_staff=False)
        self.force_login_user(user.pk)
        response = self.client.get('/api/package-handover-document-types/2/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/package-handover-document-types/2/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'name': 'Residual Risks', 'sort': '-name'},
                '/package_handover_document_type/get_all_desc_order.json',
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_handover_document_type/get_page_per_page.json',
            ),
            (
                {'search': 'tion'},
                '/package_handover_document_type/search.json',
            ),
            (
                {'user_group': 4},
                '/package_handover_document_type/filter_by_user_group.json',
            ),
            (
                {'group': [3], 'sort': 'name'},
                '/package_handover_document_type/filter_by_group.json',
            ),
            (
                {'package': [4], 'sort': 'name'},
                '/package_handover_document_type/filter_by_package.json',
            ),
            (
                {'package_activity': [2], 'sort': 'name'},
                '/package_handover_document_type/filter_by_package_activity.json',
            ),
            (
                {'configuration_mode': True, 'sort': 'name', 'all': 1},
                '/package_handover_document_type/get_for_configuration_mode.json',
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/package-handover-document-types/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_staff(self, filters, fixture):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/package-handover-document-types/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_search(self):
        response = self.client.get('/api/package-handover-document-types/', {'search': 'tion'})

        self.assertUnauthorized(response)

    def get_filters_with_handover_documents(self):
        return (
            (
                {'has_handover_documents': True, 'package_activity': 2},
                '/package_handover_document_type/filter_with_handover_documents_by_package_activity.json'
            ),
            (
                {'has_handover_documents': True, 'package': 3},
                '/package_handover_document_type/filter_with_handover_documents_by_package.json'
            ),
            (
                {'has_handover_documents': True, 'building': 'Building A', 'all': 1},
                '/package_handover_document_type/filter_by_building.json',
            ),
            (
                {'has_handover_documents': True, 'level': '8Y', 'all': 1},
                '/package_handover_document_type/filter_by_level.json',
            ),
            (
                {'has_handover_documents': True, 'area': 'Stanford', 'all': 1},
                '/package_handover_document_type/filter_by_area.json',
            ),
        )

    @data_provider(get_filters_with_handover_documents)
    def test_get_for_project_by_multiplex(self, filters, fixture):
        self._log_in_as_staff()
        response = self.client.get('/api/projects/5/package-handover-document-types/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_get_for_project_by_consultant(self):
        staff = self._get_consultant(project=5)
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-handover-document-types/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_for_project_by_consultant.json')

    def test_get_for_project_by_subcontractor(self):
        staff = self._get_subcontractor(project=5)
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-handover-document-types/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_for_project_by_subcontractor.json')

    def test_get_for_project_with_handover_documents_by_consultant(self):
        staff = self._get_consultant(project=5)
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-handover-document-types/', {'has_handover_documents': 1})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_for_project_with_handover_documents_by_consultant.json')

    def test_get_for_project_with_handover_documents_by_subcontractor(self):
        staff = self._get_subcontractor(project=5)
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-handover-document-types/', {'has_handover_documents': 1})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_type/get_for_project_with_handover_documents_by_subcontractor.json')
