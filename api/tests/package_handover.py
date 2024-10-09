import pendulum
from unittest import mock

from django.core.files.storage import FileSystemStorage
from django.db.models import Q

from api.models import User, PackageMatrix, LocationMatrixPackage
from api.models.package_handover import PackageHandover
from api.tests.test import TestCase, data_provider


class PackageHandoverTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/package_handovers.json',
        'api/tests/fixtures/dumps/package_handover_document.json'
    ]
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-matrix/', {'package': 2, 'package_activity': [3, 5]})

        self.assertCreated(response)
        # Check that deleted matrix restored
        self.assertDatabaseHas(PackageMatrix, {'project': 5, 'package': 2, 'package_activity': 3})
        self.assertDatabaseHas(PackageMatrix, {'project': 5, 'package': 2, 'package_activity': 5})
        self.assertDatabaseHas(LocationMatrixPackage, {'package_matrix__package_activity': 5, 'enabled': True,
                                                       'package_matrix__package': 2})
        self.assertDatabaseHas(PackageHandover, {'package_matrix__package_activity': 5, 'package_matrix__package': 2})
        # Make sure that package handover didn't create for package activity without ticked location matrices.
        self.assertDatabaseMissing(PackageHandover, {'package_matrix__package_activity': 3,
                                                     'package_matrix__package': 2})

        self.assertEventsExist('/package_handover/create_events_assertion.json')

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandover, {'pk': 2, **update_package_handover})

    def test_update_by_staff(self):
        project_staff = self._get_staff(project=5)
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandover, {'pk': 2, **update_package_handover})

    def test_update_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        update_package_handover = self.load_request_fixture('/package_handover/update_package_handover.json')

        self.force_login_user(project_subcontractor.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertOk(response)
        self.assertDatabaseHas(PackageHandover, {'pk': 2,
                                                 'inspection_period': update_package_handover['inspection_period'],
                                                 'maintenance_period': update_package_handover['maintenance_period']})

    def test_forbid_update_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover.json')

        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertForbidden(response)

    def test_forbid_update_by_staff_from_other_project(self):
        project_staff = self._get_staff(project=5)
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/6/package-handovers/1/', update_package_handover)

        self.assertForbidden(response)

    def test_forbid_update_by_consultant(self):
        project_staff = self._get_consultant(project=5)
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertForbidden(response)

    def test_forbid_update_by_wrong_period_values(self):
        project_staff = self._get_staff(project=5)
        update_package_handover = self.load_request_fixture(
            '/package_handover/update_package_handover_by_wrong_period_values.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/package-handovers/2/', update_package_handover)

        self.assertBadRequest(response)

    def get_filters_for_search(self):
        return (
            (
                {
                    'all': True,
                    'show_all_groups': True,
                    'show_document_group': [2],
                    'expand': [
                        'expanded_package_handover_document_media.expanded_media',
                        'expanded_package_handover_document_media.expanded_upload_update',
                        'expanded_package_handover_document_type.expanded_group'
                    ]
                },
                '/package_handover/get_with_filtered_displaying_group.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': [
                        'expanded_package_handover_document_media.expanded_media',
                        'expanded_package_handover_document_media.expanded_upload_update',
                        'expanded_package_handover_document_type.expanded_group'
                    ]
                },
                '/package_handover/get_all_by_superuser.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': [
                        'expanded_package_handover_document_media.expanded_media',
                        'expanded_package_handover_document_media.expanded_upload_update',
                        'expanded_package_handover_document_type.expanded_group'
                    ]
                },
                '/package_handover/get_all_by_client.json',
                {'project__pk': 5, 'groups__pk': User.Group.CLIENT.value},
                {'project_pk': 5}
            ),
            (
                {'all': True, 'expand': 'expanded_package_handover_document_media.expanded_media'},
                '/package_handover/get_all_by_staff.json',
                {'project__pk': 5, 'groups__pk': User.Group.ADMIN.value},
                {'project_pk': 5}
            ),
            (
                {'all': True, 'expand': 'expanded_package_handover_document_media.expanded_media'},
                '/package_handover/get_all_by_subcontractor.json',
                {'project__pk': 5, 'groups__pk': User.Group.SUBCONTRACTOR.value},
                {'project_pk': 5}
            ),
            (
                {'page': 1, 'per_page': 5},
                '/package_handover/get_page_by_superuser.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'show_all_groups': True,
                    'expand': 'expanded_package_handover_document_media'
                },
                '/package_handover/get_all_by_superuser_with_expanded_last_update.json',
                {'is_superuser': True},
                {'project_pk': 1}
            ),
            (
                {
                    'all': True,
                    'expand': 'expanded_package_handover_document_media',
                    'package': [4]
                },
                '/package_handover/get_filtered_by_package.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'show_all_groups': True,
                    'expand': 'expanded_package_handover_document_media',
                    'package_activity': [2]
                },
                '/package_handover/get_filtered_by_package_activity.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': 'expanded_package_handover_document_media',
                    'package_handover_document_type': [9]
                },
                '/package_handover/get_filtered_by_document_type.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': 'expanded_package_handover_document_media',
                    'document_group': [2]
                },
                '/package_handover/get_filtered_by_document_group.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': 'expanded_package_handover_document_media',
                    'status': ['requesting_approval']
                },
                '/package_handover/get_filtered_by_status.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'show_all_groups': True,
                    'expand': 'expanded_package_handover_document_media',
                },
                '/package_handover/get_with_empty_groups.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {'company': [2]},
                '/package_handover/filter_by_company.json',
                {'is_superuser': True},
                {'project_pk': 5}
            ),
            (
                {
                    'all': True,
                    'expand': 'expanded_package_handover_document_media',
                },
                '/package_handover/get_all_by_consultant.json',
                {'pk': self._get_consultant(project=5).pk},
                {'project_pk': 5}
            ),
        )

    @data_provider(get_filters_for_search)
    def test_search(self, filters, fixture, user_params, package_handover_params):
        user = self._get_user(**user_params)
        self.force_login_user(user.pk)
        response = self.client.get('/api/projects/%s/package-handovers/' % package_handover_params['project_pk'], filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_superuser(self):
        self._log_in_as_superuser()
        response = self.client.get('/api/package-activities/', {
            'expand': ['expanded_package_handover'],
            'all': True,
            'project': 5
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover/get_all_with_expanded_package_handover.json')

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad+1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/package-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['wrap.trap1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/package-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.subcontractor@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_client(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_client(project=5)
        response = self.client.get('/api/projects/5/package-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.client@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_handover/csv_report_created.html'
            }
        ])

    def test_delete_and_restore_on_location_matrix_package_change(self):
        project_staff = self._get_staff(project=5, editmode__project=5)
        sync_data = self.load_request_fixture('/package_handover/delete_and_restore_on_location_matrix_package_change.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertOk(response)
        self.assertSoftDeleted(PackageHandover, 2)
        self.assertDatabaseHas(PackageHandover, {'package_matrix': 4})

    def test_delete_and_restore_on_location_matrix_change(self):
        payload = self.load_request_fixture('/package_handover/delete_and_restore_on_location_matrix_change.json')
        project_staff_in_edit_mode = self._get_staff(project=5, editmode__project=5)

        self.force_login_user(project_staff_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix/sync/', payload)

        self.assertOk(response)
        self.assertSoftDeleted(PackageHandover, 4)
        self.assertDatabaseHas(PackageHandover, 7)
