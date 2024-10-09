from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import Company, User, PackageHandoverDocumentMedia, AssetHandoverDocumentMedia
from api.tests.test import TestCase, data_provider


class CompaniesTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/companies.json']
    PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES = 5
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def setUp(self) -> None:
        super().setUp()
        self.superuser = User.objects.filter(is_superuser=True).first()

    def get_non_superusers(self):
        non_superusers = User.objects.filter(is_superuser=False).order_by('groups__pk').distinct('groups__pk').all()
        return [user.pk for user in non_superusers]

    def test_create(self):
        new_company = self.load_request_fixture('/companies/create_company.json')

        self.force_login_user(self.superuser.pk)
        response = self.client.post('/api/companies/', new_company)

        self.assertCreated(response)
        self.assertDatabaseHas(Company, new_company)
        self.assertEventsExist('/companies/create_company_events_assertion.json')

    @data_provider(get_non_superusers)
    def test_forbid_create(self, user):
        new_company = self.load_request_fixture('/companies/create_company.json')

        self.force_login_user(user)
        response = self.client.post('/api/companies/', new_company)

        self.assertForbidden(response)

    def test_update(self):
        update_company = self.load_request_fixture('/companies/update_company.json')

        self.force_login_user(self.superuser.pk)
        response = self.client.put('/api/companies/2/', update_company)

        self.assertOk(response)
        self.assertDatabaseHas(Company, {'pk': 2, **update_company})
        self.assertEventsExist('/companies/update_company_events_assertion.json')

    @data_provider(get_non_superusers)
    def test_forbid_update(self, user):
        update_company = self.load_request_fixture('/companies/update_company.json')

        self.force_login_user(user)
        response = self.client.put('/api/companies/1/', update_company)

        self.assertForbidden(response)

    def test_dont_allow_delete(self):
        # don't allow to delete company if there are users attached to it
        self.force_login_user(self.superuser.pk)
        response = self.client.delete('/api/companies/2/')

        self.assertBadRequest(response)

    def test_delete(self):
        self.force_login_user(self.superuser.pk)
        response = self.client.delete('/api/companies/6/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(Company, 6)
        self.assertEventsExist('/companies/delete_companies_events_assertion.json')

    @data_provider(get_non_superusers)
    def test_forbid_delete(self, user):
        self.force_login_user(user)
        response = self.client.delete('/api/companies/3/')

        self.assertForbidden(response)

    @data_provider(get_non_superusers)
    def test_get(self, user):
        self.force_login_user(user)
        response = self.client.get('/api/companies/2/', {'expand': ['expanded_users_count']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_company.json')

    def test_get_via_api_key(self):
        response = self.client.get('/api/companies/2/', {'expand': ['expanded_users_count']},
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_company.json')

    def test_forget_get_via_invalid_api_key(self):
        response = self.client.get('/api/companies/2/', {'expand': ['expanded_users_count']},
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfudcK6gvx5yrSS302S4Faw6hY6w')

        self.assertUnauthorized(response)

    def test_forbid_get(self):
        response = self.client.get('/api/companies/2/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': '-name'},
                '/companies/get_all_desc_order.json',
            ),
            (
                {'page': 2, 'per_page': 2},
                '/companies/get_page_per_page.json',
            ),
            (
                {'search': 'isn'},
                '/companies/search.json',
            ),
            (
                {'subcontractors_in_project': 1},
                '/companies/get_by_subcontractors_in_project.json',
            ),
            (
                {'clients_in_project': 5},
                '/companies/get_by_clients_in_project.json',
            ),
            (
                {'name': '20 Century Fox'},
                '/companies/get_by_name.json',
            ),
            (
                {'companies_of_package_activities': 3, 'project': 1},
                '/companies/filter_by_package_activity.json'
            ),
            (
                {'companies_of_package_activities': 4, 'project': 1},
                '/companies/filter_by_package_activity_with_default_result.json'
            ),
            (
                {'id': [3, 4]},
                '/companies/filter_by_id.json'
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture):
        users = self.get_non_superusers() + [self.superuser.pk]
        for user in users:
            self.force_login_user(user)
            response = self.client.get('/api/companies/', filters)

            self.assertOk(response)
            self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_search(self):
        response = self.client.get('/api/companies/')

        self.assertUnauthorized(response)

    @data_provider(get_filters)
    def test_search_via_api_key(self, filters, fixture):
        response = self.client.get('/api/companies/', filters,
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_handover_documents(self):
        return (
            (
                {'has_handover_documents': True},
                '/companies/get_with_handover_documents.json'
            ),
            (
                {'has_handover_documents': True, 'building': ['Building A']},
                '/companies/get_with_handover_documents_filtered_by_building.json'
            ),
            (
                {'has_handover_documents': True, 'level': ['A']},
                '/companies/get_with_handover_documents_filtered_by_level.json'
            ),
            (
                {'has_handover_documents': True, 'area': ['Hall']},
                '/companies/get_with_handover_documents_filtered_by_area.json'
            ),
            (
                {'has_handover_documents': True, 'package': [3]},
                '/companies/get_with_handover_documents_filtered_by_package.json'
            ),
            (
                {'has_handover_documents': True, 'package_activity': [4]},
                '/companies/get_with_handover_documents_filtered_by_package_activity.json'
            ),
            (
                {'has_handover_documents': True, 'asset_handover_document_type': [2]},
                '/companies/get_with_handover_documents_filtered_by_document_type.json'
            ),
        )

    @data_provider(get_filters_for_handover_documents)
    def test_list_handover_document_companies(self, filters, fixture):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_handover_document_companies_by_project_admin(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_admin(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_with_handover_documents_by_project_admin.json')

    def test_list_handover_document_companies_by_project_manager(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_manager(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_with_handover_documents_by_project_manager.json')

    def test_list_handover_document_companies_by_project_client(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_client(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_with_handover_documents_by_project_client.json')

    def test_list_handover_document_companies_by_non_project_admin(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_admin(~Q(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES))
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertForbidden(response)

    def test_list_handover_document_companies_by_non_project_manager(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_manager(~Q(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES))
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertForbidden(response)

    def test_list_handover_document_companies_by_project_consultant(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_consultant(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertForbidden(response)

    def test_list_handover_document_companies_by_project_subcontractor(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        self._log_in_as_subcontractor(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertForbidden(response)

    def filters_for_asset_handover_company_list(self):
        return [
            ({'package': [4]},
             '/companies/get_with_asset_handover_company_filter_by_package.json'),
            ({'package_activity': [2]},
             '/companies/get_with_asset_handover_company_filter_by_package_activity.json'),
            ({'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL},
             '/companies/get_with_asset_handover_company_filter_by_status.json'),
            ({'document_type': [2]},
             '/companies/get_with_asset_handover_company_filter_by_document_type.json'),
            ({'asset_handover__location_matrix__building': ['Building A']},
             '/companies/get_with_asset_handover_company_filter_by_building.json'),
            ({'asset_handover__location_matrix__level': ['7A']},
             '/companies/get_with_asset_handover_company_filter_by_level.json'),
            ({'asset_handover__location_matrix__area': ['Hall']},
             '/companies/get_with_asset_handover_company_filter_by_area.json'),
        ]

    @data_provider(filters_for_asset_handover_company_list)
    def test_company_admin_get_asset_handover_companies_by_filter(self, filters, fixture):
        self._log_in_as_company_admin()

        url = reverse('asset_handover_company_list', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(filters_for_asset_handover_company_list)
    def test_project_admin_get_asset_handover_companies_by_filter(self, filters, fixture):
        self._log_in_as_admin(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)

        url = reverse('asset_handover_company_list', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_list_handover_document_companies(self):
        url = reverse('handover_document-companies', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertUnauthorized(response)

    def test_get_package_handover_companies(self):
        self._log_in_as_admin(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)

        url = reverse('package_handover_companies-list', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/companies/get_with_package_handover_all_companies.json')

    def filters_for_package_handover_company_list(self):
        return [
            ({'package': [3]},
             '/companies/get_with_package_handover_filter_by_package.json'),
            ({'package_activity': [5]},
             '/companies/get_with_package_handover_filter_by_package_activity.json'),
            ({'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS},
             '/companies/get_with_package_handover_filter_by_status.json'),
            ({'document_group': [2]},
             '/companies/get_with_package_handover_filter_by_document_group.json'),
            ({'document_type': [1]},
             '/companies/get_with_package_handover_filter_by_document_type.json'),
        ]

    @data_provider(filters_for_package_handover_company_list)
    def test_company_admin_get_package_handover_companies_by_filter(self, filters, fixture):
        self._log_in_as_company_admin()

        url = reverse('package_handover_companies-list', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(filters_for_package_handover_company_list)
    def test_project_admin_get_package_handover_companies_by_filter(self, filters, fixture):
        self._log_in_as_admin(project=self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES)

        url = reverse('package_handover_companies-list', kwargs={'project_pk': self.PROJECT_FOR_HANDOVER_DOCUMENT_COMPANIES})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('company_generate_csv'))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Company CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/companies/csv_report_created.html'
            }
        ])
