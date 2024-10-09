from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import Package
from api.tests.test import TestCase, data_provider


class PackageTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/packages.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package = self.load_request_fixture('/package/new_package.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/packages/', new_package)

        self.assertCreated(response)
        self.assertDatabaseHas(Package, {'name': 'Twelve package'})
        self.assertEventsExist('/package/create_events_assertion.json')

    def test_forbid_create_by_non_superuser(self):
        non_superuser = self._get_staff()
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/packages/1/')

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        response = self.client.get('/api/packages/1/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/packages/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/get_package.json')

    def test_forbid_get_by_staff(self):
        non_superuser = self._get_staff()
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/packages/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/packages/1/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/packages/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Package, 1)
        self.assertEventsExist('/package/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_staff()
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/packages/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/packages/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_package = self.load_request_fixture('/package/update_package.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/1/', update_package)

        self.assertOk(response)
        self.assertDatabaseHas(Package, {'name': 'Updated first package', 'pk': 1})
        self.assertEventsExist('/package/update_events_assertion.json')

    def test_forbid_update_by_non_superuser(self):
        non_superuser = self._get_staff()
        update_package = self.load_request_fixture('/package/update_package.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/packages/1/', update_package)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package = self.load_request_fixture('/package/update_package.json')
        response = self.client.put('/api/packages/1/', update_package)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'expand': 'expanded_projects_count'},
                '/package/get_all.json'
            ),
            (
                {'all': True, 'sort': '-order'},
                '/package/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package/get_all_page_per_page.json'
            ),
            (
                {'exclude_bound_with_project': 5},
                '/package/get_all_excluded_for_project.json',
            ),
        )

    @data_provider(get_filters)
    def test_search_as_staff(self, filters, fixture):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/packages/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_staff(self):
        non_staff = self._get_user(is_staff=False)
        self.force_login_user(non_staff.pk)
        response = self.client.get('/api/packages/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/packages/', {'all': 1})

        self.assertUnauthorized(response)

    def test_sync_by_superuser(self):
        request = self.load_request_fixture('/package/sync_only_existing_packages_order.json')
        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/?sort=order', request)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/synced_response.json')
        self.assertDatabaseHas(Package, {'pk': 1, 'order': 1})
        self.assertDatabaseHas(Package, {'pk': 2, 'order': 2})
        self.assertDatabaseHas(Package, {'pk': 3, 'order': 3})
        self.assertDatabaseHas(Package, {'pk': 4, 'order': 4})
        self.assertDatabaseHas(Package, {'pk': 5, 'order': 5})
        self.assertDatabaseHas(Package, {'pk': 6, 'order': 6})
        self.assertDatabaseHas(Package, {'pk': 7, 'order': 7})
        self.assertEventsExist('/package/sync_events_assertion.json')

    def test_sync_with_empty_data_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/synced_with_empty_data_response.json')
        self.assertSoftDeleted(Package, 1)
        self.assertSoftDeleted(Package, 2)
        self.assertSoftDeleted(Package, 3)
        self.assertSoftDeleted(Package, 4)
        self.assertSoftDeleted(Package, 5)
        self.assertSoftDeleted(Package, 6)
        self.assertSoftDeleted(Package, 7)
        self.assertEventsExist('/package/sync_with_empty_data_events_assertion.json')

    def test_sync_with_non_existing_id_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/', [{'id': 100, 'order': 500}])

        self.assertBadRequest(response)

    def test_forbid_sync_by_non_superuser(self):
        request = self.load_request_fixture('/package/sync_only_existing_packages_order.json')
        non_superuser = self._get_staff()

        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/packages/', request)

        self.assertForbidden(response)

    def test_unauthorized_sync(self):
        request = self.load_request_fixture('/package/sync_only_existing_packages_order.json')
        response = self.client.put('/api/packages/', request)

        self.assertUnauthorized(response)

    def test_sync_with_creation_and_update_by_superuser(self):
        superuser = self._get_superuser()
        request = self.load_request_fixture('/package/sync_existing_removed_and_new_packages.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/', request)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/synced_with_creation_and_update_response.json')
        self.assertSoftDeleted(Package, 7)
        self.assertSoftDeleted(Package, 6)
        self.assertDatabaseHas(Package, {'pk': 1, 'order': 1, 'name': 'Thor'})
        self.assertDatabaseHas(Package, {'pk': 2, 'order': 3})
        self.assertDatabaseHas(Package, {'pk': 3, 'order': 4})
        self.assertDatabaseHas(Package, {'pk': 4, 'order': 5})
        self.assertDatabaseHas(Package, {'pk': 5, 'order': 6})
        self.assertDatabaseHas(Package, {'order': 8, 'name': 'Eight package'})
        self.assertDatabaseHas(Package, {'order': 9, 'name': 'Nine package'})
        self.assertEventsExist('/package/sync_with_creation_and_update_events_assertion.json')

    def test_sync_with_non_unique_package_name_for_existing_by_superuser(self):
        superuser = self._get_superuser()
        request = self.load_request_fixture('/package/sync_with_non_unique_package_name_for_existing.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/', request)

        self.assertBadRequest(response)

    def test_sync_with_existing_package_name_for_new(self):
        superuser = self._get_superuser()
        request = self.load_request_fixture('/package/sync_with_non_unique_package_name_for_new.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/', request)

        self.assertBadRequest(response)

    def test_sync_with_same_name_like_deleted(self):
        superuser = self._get_superuser()
        request = self.load_request_fixture('/package/sync_with_same_name_like_deleted_package.json')
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/packages/', request)
        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/synced_with_same_name_like_deleted_response.json')
        self.assertSoftDeleted(Package, 7)
        self.assertSoftDeleted(Package, 6)
        self.assertDatabaseHas(Package, {'pk': 1, 'order': 1, 'name': 'Thor'})
        self.assertDatabaseHas(Package, {'pk': 2, 'order': 3})
        self.assertDatabaseHas(Package, {'pk': 3, 'order': 4})
        self.assertDatabaseHas(Package, {'pk': 4, 'order': 5, 'name': 'Seventh package'})
        self.assertDatabaseHas(Package, {'pk': 5, 'order': 6})
        self.assertDatabaseHas(Package, {'order': 8, 'name': 'Eight package'})
        self.assertDatabaseHas(Package, {'order': 9, 'name': 'Nine package'})
        self.assertDatabaseHas(Package, {'order': 7, 'name': 'Sixth package'})
        self.assertEventsExist('/package/sync_with_same_name_like_deleted_events_assertion.json')

    def test_forbid_get_project_package_matrix_packages_by_non_project_consultant(self):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        self._log_in_as_consultant(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_forbid_get_project_package_matrix_packages_by_non_project_subcontractor(self):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        self._log_in_as_subcontractor(~Q(project=5))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_project_package_matrix_packages_by_project_client(self):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        self._log_in_as_client(project=5)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/get_package_matrix_packages_by_client.json')

    def test_forbid_get_project_package_matrix_packages_by_client_from_other_project(self):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 7})
        self._log_in_as_client(~Q(project=7))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_unauthorized_get_project_package_matrix_packages(self):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 7})
        response = self.client.get(url)

        self.assertUnauthorized(response)

    def test_list_with_handover_documents_by_superuser(self):
        self._log_in_as_superuser()
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        response = self.client.get(url, {'has_handover_documents': True, 'building': 'Building I'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/list_with_handover_documents_by_superuser.json')

    def test_list_with_handover_documents_by_consultant(self):
        self._log_in_as_consultant(project=5)
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/list_with_handover_documents_by_consultant.json')

    def test_list_with_handover_documents_by_subcontractor(self):
        self._log_in_as_subcontractor(project=5)
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        response = self.client.get(url, {'has_handover_documents': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package/list_with_handover_documents_by_subcontractor.json')

    def get_filters_for_package_matrix_package(self):
        return (
            (
                {'building': ['Building F']},
                '/package/get_all_by_building.json',
            ),
            (
                {'level': ['-3']},
                '/package/get_all_by_level.json',
            ),
            (
                {'area': ['Group']},
                '/package/get_all_by_area.json',
            ),
            (
                {'package_handover_document_type': [9]},
                '/package/get_filtered_by_document_type.json',
            ),
            (
                {'has_package_handover_documents': True},
                '/package/get_with_package_handover_documents.json',
            ),
            (
                {'has_asset_handovers': True},
                '/package/get_with_asset_handovers.json',
            ),
            (
                {'has_published_tasks': True},
                '/package/get_with_published_tasks.json',
            ),
        )

    @data_provider(get_filters_for_package_matrix_package)
    def test_get_project_package_matrix_packages_by_superuser(self, filters, fixture):
        url = reverse('package_matrix_packages-list', kwargs={'project_pk': 5})
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('package_generate_csv'))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package/csv_report_created.html'
            }
        ])
