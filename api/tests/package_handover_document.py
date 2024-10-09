from api.tests.test import TestCase, data_provider
from api.models.package_handover import PackageHandoverDocument


class PackageHandoverDocumentTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_handovers.json', 'api/tests/fixtures/dumps/package_handover_document.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document = self.load_request_fixture('/package_handover_document/create_package_handover_document.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-handover-documents/', new_package_handover_document)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocument, new_package_handover_document)

    def test_create_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document = self.load_request_fixture('/package_handover_document/create_package_handover_document.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-documents/', new_package_handover_document)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocument, new_package_handover_document)

    def test_forbid_create(self):
        project_staff = self._get_staff(project=4)
        new_package_handover_document = self.load_request_fixture('/package_handover_document/forbid_create_package_handover_document.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/3/package-handover-documents/', new_package_handover_document)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_handover_document = self.load_request_fixture('/package_handover_document/create_package_handover_document.json')
        response = self.client.post('/api/projects/5/package-handover-documents/', new_package_handover_document)

        self.assertUnauthorized(response)

    def test_update(self):
        superuser = self._get_superuser()
        update_package_handover_document = self.load_request_fixture('/package_handover_document/update_package_handover_document.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/package-handover-documents/2/', update_package_handover_document)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandoverDocument, {'pk': 2, **update_package_handover_document})

    def test_update_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        update_package_handover_document = self.load_request_fixture('/package_handover_document/update_package_handover_document.json')

        response = self.client.put('/api/projects/5/package-handover-documents/2/', update_package_handover_document)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandoverDocument, {'pk': 2, **update_package_handover_document})

    def test_forbid_update(self):
        update_package_handover = self.load_request_fixture('/package_handover_document/update_package_handover_document.json')

        project_staff = self._get_staff(project=4)
        self.force_login_user(project_staff.pk)

        response = self.client.put('/api/projects/3/package-handover-documents/6/', update_package_handover)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package_handover_document = self.load_request_fixture('/package_handover_document/update_package_handover_document.json')
        response = self.client.put('/api/projects/5/package-handover-documents/2/', update_package_handover_document)

        self.assertUnauthorized(response)

    def test_delete(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/package-handover-documents/2/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(PackageHandoverDocument, 2)

    def test_delete_by_staff(self):
        project_staff = self._get_staff(project=6)
        self.force_login_user(project_staff.pk)

        response = self.client.delete('/api/projects/5/package-handover-documents/2/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(PackageHandoverDocument, 2)

    def test_forbid_delete(self):
        project_staff = self._get_staff(project=4)
        self.force_login_user(project_staff.pk)

        response = self.client.delete('/api/projects/3/package-handover-documents/6/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/package-handover-documents/2/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handover-documents/2/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document/get_package_handover_document.json')

    def test_get_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/5/package-handover-documents/2/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document/get_package_handover_document.json')

    def test_forbid_get(self):
        project_staff = self._get_staff(project=4)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/3/package-handover-documents/6/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/package-handover-documents/2/')

        self.assertUnauthorized(response)

    def get_filters_for_superuser(self):
        return (
            (
                {'all': True},
                '/package_handover_document/get_all_by_superuser.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_handover_document/get_page_by_superuser.json',
            ),
            (
                {'package_activity': [1, 2]},
                '/package_handover_document/filter_by_package_activity.json'
            ),
            (
                {'project': [5]},
                '/package_handover_document/filter_by_project.json'
            ),
            (
                {'company': [2]},
                '/package_handover_document/filter_by_company.json'
            ),
        )

    @data_provider(get_filters_for_superuser)
    def test_search(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handover-documents/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_staff(self):
        return (
            (
                {'all': True},
                '/package_handover_document/get_all_by_staff.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_handover_document/get_page_by_staff.json',
            ),
        )

    @data_provider(get_filters_for_staff)
    def test_search_by_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-handover-documents/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_staff)
    def test_forbid_search_by_staff(self, filters, _fixture):
        project_staff = self._get_staff(project=4)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/3/package-handover-documents/', filters)

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/package-handover-documents/', {'search': 'sub'})

        self.assertUnauthorized(response)

    def test_search_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/package-handover-documents/', {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document/search_by_consultant.json')

    def test_search_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/package-handover-documents/', {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document/search_by_subcontractor.json')
