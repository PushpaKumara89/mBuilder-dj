from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.urls import reverse

from api.models import LocationMatrixPackage, Task, Subtask
from api.tests.test import TestCase, data_provider


class LocationMatrixPackagesTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/location_matrix_package.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create_by_project_staff(self):
        new_location_matrix_package = self.load_request_fixture('/location_matrix_package/new_location_matrix_package.json')
        project_staff = self._get_staff(project=5)

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/', new_location_matrix_package)

        self.assertCreated(response)
        self.assertDatabaseHas(LocationMatrixPackage, {**new_location_matrix_package, 'package_activity': 1,
                                                       'package_activity_name': 'First package activity', 'package': 4})

    def test_create_by_superuser(self):
        new_location_matrix_package = self.load_request_fixture('/location_matrix_package/new_location_matrix_package.json')
        project_staff = self._get_superuser(~Q(project=5))

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/', new_location_matrix_package)

        self.assertCreated(response)
        self.assertDatabaseHas(LocationMatrixPackage, {**new_location_matrix_package, 'package_activity': 1,
                                                       'package_activity_name': 'First package activity', 'package': 4})

    def test_forbid_create_not_in_edit_mode(self):
        new_location_matrix_package = self.load_request_fixture('/location_matrix_package/new_location_matrix_package.json')
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=5), project=5)

        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/', new_location_matrix_package)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_location_matrix_package = self.load_request_fixture('/location_matrix_package/new_location_matrix_package.json')
        response = self.client.post('/api/projects/5/location-matrix-packages/', new_location_matrix_package)

        self.assertUnauthorized(response)

    def test_update_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        update_location_matrix = self.load_request_fixture('/location_matrix_package/update_location_matrix_package.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/1/', update_location_matrix)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrixPackage, {**update_location_matrix, 'package': 4, 'package_activity': 1,
                                                       'package_activity_name': 'First package activity', 'pk': 1})

    def test_update_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5))
        update_location_matrix = self.load_request_fixture('/location_matrix_package/update_location_matrix_package.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/1/', update_location_matrix)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrixPackage, {**update_location_matrix, 'package': 4, 'package_activity': 1,
                                                       'package_activity_name': 'First package activity', 'pk': 1})

    def test_forbid_update_by_staff_from_other_project(self):
        staff_from_other_project = self._get_staff(~Q(project=5), editmode__project=5)
        update_location_matrix = self.load_request_fixture('/location_matrix_package/update_location_matrix_package.json')

        self.force_login_user(staff_from_other_project.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/1/', update_location_matrix)

        self.assertForbidden(response)

    def test_forbid_update_not_in_edit_mode(self):
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=5), project=5)
        update_location_matrix = self.load_request_fixture('/location_matrix_package/update_location_matrix_package.json')

        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/1/', update_location_matrix)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_location_matrix = self.load_request_fixture('/location_matrix_package/update_location_matrix_package.json')
        response = self.client.put('/api/projects/5/location-matrix-packages/1/', update_location_matrix)

        self.assertUnauthorized(response)

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/location-matrix-packages/1/')

        self.assertNoContent(response)

        self.assertDatabaseMissing(LocationMatrixPackage, 1)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5), editmode__project=5)
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/location-matrix-packages/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(LocationMatrixPackage, 1)

    def test_forbid_delete_by_project_staff_not_in_edit_mode(self):
        project_staff = self._get_staff(~Q(editmode__project=5), project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/location-matrix-packages/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/location-matrix-packages/1/')

        self.assertUnauthorized(response)

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/1/', {'expand': 'expanded_media'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix_package/get_location_matrix_package.json')

    def test_get_by_api_key(self):
        response = self.client.get('/api/projects/5/location-matrix-packages/1/', {'expand': 'expanded_media'},
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix_package/get_location_matrix_package.json')

    def test_get_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5))
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/1/', {'expand': 'expanded_media'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix_package/get_location_matrix_package.json')

    def test_forbid_get_by_staff_from_another_project(self):
        project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/location-matrix-packages/1/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': '-location_matrix'},
                '/location_matrix_package/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2, 'sort': '-location_matrix'},
                '/location_matrix_package/get_page_per_page.json'
            ),
            (
                {'package': 4, 'sort': '-location_matrix'},
                '/location_matrix_package/filter_by_package.json'
            ),
            (
                {'building': 'Building A', 'sort': '-location_matrix'},
                '/location_matrix_package/filter_by_building.json'
            ),
            (
                {'level': 'A', 'sort': '-location_matrix'},
                '/location_matrix_package/filter_by_level.json'
            ),
            (
                {'area': 'Hall', 'sort': '-location_matrix'},
                '/location_matrix_package/filter_by_area.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_api_key(self, filters, fixture):
        response = self.client.get('/api/projects/5/location-matrix-packages/', filters,
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser(~Q(project=5))
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_staff_from_another_project(self):
        another_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(another_project_staff.pk)
        response = self.client.get('/api/projects/5/location-matrix-packages/', {'all': 1})

        self.assertForbidden(response)

    def test_sync_by_project_staff(self):
        project_staff = self._get_staff(project=5, editmode__project=5)
        sync_data = self.load_request_fixture('/location_matrix_package/sync_location_matrix_package.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix_package/sync_all.json')

        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 1, 'enabled': True})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 2, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 3, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 4, 'enabled': True})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 5, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 6, 'enabled': True})

        self.assertSoftDeleted(Task, 1)
        self.assertDatabaseHas(Subtask, 1)

        self.assertHardDeleted(Task, 2)
        self.assertHardDeleted(Subtask, 2)

        self.assertDatabaseHas(Task, 3)
        self.assertDatabaseHas(Subtask, 3)

        self.assertEventsExist('/location_matrix_package/sync_events_assertion.json')

    def test_sync_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5), editmode__project=5)
        sync_data = self.load_request_fixture('/location_matrix_package/sync_location_matrix_package.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertOk(response)

    def test_forbid_sync_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=5), editmode__project=5)
        sync_data = self.load_request_fixture('/location_matrix_package/sync_location_matrix_package.json')

        self.force_login_user(other_project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertForbidden(response)

    def test_add_media_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/add/', {'media': [3, 4]})

        self.assertOk(response)

        self.assertDatabaseHas(LocationMatrixPackage, {'media__pk': 3, 'pk': 2})
        self.assertDatabaseHas(LocationMatrixPackage, {'media__pk': 4, 'pk': 2})

    def test_add_media_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5), editmode__project=5)
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/add/', {'media': [3, 4]})

        self.assertOk(response)

        self.assertDatabaseHas(LocationMatrixPackage, {'media__pk': 3, 'pk': 2})
        self.assertDatabaseHas(LocationMatrixPackage, {'media__pk': 4, 'pk': 2})

    def test_forbid_add_media_by_project_staff_not_in_edit_mode(self):
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=5), project=5)
        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/add/', {'media': [3, 4]})

        self.assertForbidden(response)

    def test_unauthorized_add_media(self):
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/add/', {'media': [3, 4]})

        self.assertUnauthorized(response)

    def test_remove_media_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/remove/', {'media': [1, 2]})

        self.assertOk(response)

        self.assertHardDeleted(LocationMatrixPackage, {'media__pk': 1, 'pk': 2})
        self.assertHardDeleted(LocationMatrixPackage, {'media__pk': 2, 'pk': 2})

    def test_remove_media_by_superuser(self):
        superuser = self._get_superuser(~Q(project=5), editmode__project=5)
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/remove/', {'media': [1, 2]})

        self.assertOk(response)

        self.assertHardDeleted(LocationMatrixPackage, {'media__pk': 1, 'pk': 2})
        self.assertHardDeleted(LocationMatrixPackage, {'media__pk': 2, 'pk': 2})

    def test_forbid_remove_media_by_project_staff_not_in_edit_mode(self):
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=5), project=5)
        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/remove/', {'media': [1, 2]})

        self.assertForbidden(response)

    def test_unauthorized_remove_media(self):
        response = self.client.post('/api/projects/5/location-matrix-packages/2/media/remove/', {'media': [1, 2]})

        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('location_matrix_packages_generate_csv', kwargs={'project_pk': 5}))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Location Matrix Package CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/location_matrix_package/csv_report_created.html'
            }
        ])
