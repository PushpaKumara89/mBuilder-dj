from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import Task, LocationMatrixPackage, TaskUpdate
from api.tests.test import TestCase, data_provider


class TaskTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/tasks.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def mock_function_with_arguments(self, *args, **kwargs):
        return

    def mock_save_report(self, *args, **kwargs):
        class MediaMock(object):
            pass

        mock_object = MediaMock()
        mock_object.link = 'http://localhost/image.jpg'

        return mock_object

    def test_create(self):
        project_staff = self._get_staff(project=5)
        sync_data = self.load_request_fixture('/tasks/create_tasks.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/sync_all.json')
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 1, 'enabled': True})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 2, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 3, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 4, 'enabled': True})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 5, 'enabled': False})
        self.assertDatabaseHas(LocationMatrixPackage, {'pk': 6, 'enabled': True})
        self.assertDatabaseHas(Task, {'location_matrix': 1, 'package_activity': 2, 'package_activity_task': 2, 'user': 2, 'status': Task.Statuses.ACCEPTED})
        self.assertDatabaseHas(Task, {'location_matrix': 2, 'package_activity': 3, 'package_activity_task': 3, 'user': 2, 'status': Task.Statuses.OUTSTANDING})
        self.assertDatabaseMissing(Task, {'location_matrix': 1, 'package_activity': 4, 'package_activity_task': 5})
        self.assertDatabaseMissing(Task, {'location_matrix': 2, 'package_activity': 2, 'package_activity_task': 2})
        self.assertDatabaseHas(Task, {'location_matrix': 1, 'package_activity': 4, 'package_activity_task': 4})
        self.assertDatabaseHas(TaskUpdate, {'task': 5, 'new_data': {'status': Task.Statuses.NOT_APPLICABLE}, 'old_data': {}, 'user': 2})
        self.assertEventsExist('/tasks/create_events_assertion.json')

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/2/', {'expand': ['subtasks', 'expanded_last_attachments',
                                                                           'expanded_user.expanded_user_company']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/get_task.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/2/', {'expand': ['subtasks', 'expanded_last_attachments']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/get_task_by_staff.json')

    def test_forbid_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/2/', {'expand': ['subtasks', 'expanded_last_attachments']})

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/tasks/2/', {'expand': ['subtasks', 'expanded_last_attachments']})

        self.assertUnauthorized(response)

    def test_get_assigned_users_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/get_assigned_users.json')

    def test_get_assigned_users_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/get_assigned_users.json')

    def test_forbid_get_assigned_users_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/')

        self.assertForbidden(response)

    def test_unauthorized_get_assigned_users(self):
        response = self.client.get('/api/projects/5/tasks/assigned-users/')

        self.assertUnauthorized(response)

    def get_filters_for_test_search_assigned_users(self):
        return (
            (
                {'search': 'Bartosz'},
                '/tasks/search_assigned_users_by_first_name.json'
            ),
            (
                {'search': 'Heat'},
                '/tasks/search_assigned_users_by_last_name.json'
            ),
            (
                {'search': 'cool.brad+1'},
                '/tasks/search_assigned_users_by_email.json'
            ),
        )

    @data_provider(get_filters_for_test_search_assigned_users)
    def test_search_assigned_users_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_test_search_assigned_users)
    def test_search_assigned_users_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_assigned_users_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/assigned-users/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search_assigned_users(self):
        response = self.client.get('/api/projects/5/tasks/assigned-users/', {'all': 1})

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_task = self.load_request_fixture('/tasks/update_task.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/tasks/2/', update_task)

        self.assertOk(response)
        self.assertDatabaseHas(Task, {'pk': 2, 'status': Task.Statuses.ACCEPTED.value})
        self.assertIsNotNone(Task.objects.get(pk=2).date_of_approval)
        self.assertEventsExist('/tasks/update_events_assertion.json')

    def test_update_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        update_task = self.load_request_fixture('/tasks/update_task.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/tasks/2/', update_task)

        self.assertOk(response)

    def test_forbid_update_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        update_task = self.load_request_fixture('/tasks/update_task.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.put('/api/projects/5/tasks/2/', update_task)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_task = self.load_request_fixture('/tasks/update_task.json')
        response = self.client.put('/api/projects/5/tasks/2/', update_task)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'all_with_activity': True},
                '/tasks/get_all_with_activity.json'
            ),
            (
                {'all': True},
                '/tasks/get_all.json'
            ),
            (
                {'all': True, 'expand': ['expanded_attachments', 'expanded_package_activity.expanded_description',
                                         'expanded_package_activity.expanded_description_image']},
                '/tasks/get_all_with_attachments.json'
            ),
            (
                {'building': ['Building A']},
                '/tasks/get_by_building.json'
            ),
            (
                {'area': ['Hall', 'Meeting room']},
                '/tasks/get_by_area.json'
            ),
            (
                {'level': 'A'},
                '/tasks/get_by_level.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/tasks/get_all_page_per_page.json'
            ),
            (
                {'package': 3},
                '/tasks/get_by_package.json'
            ),
            (
                {'package_activity': 2},
                '/tasks/get_by_package_activity.json'
            ),
            (
                {'package_activity_task': [2]},
                '/tasks/get_by_package_activity_task.json'
            ),
            (
                {'user': [2]},
                '/tasks/get_by_user.json'
            ),
            (
                {'status': ['not_verified', 'accepted']},
                '/tasks/get_by_status.json'
            ),
            (
                {'search': 'build'},
                '/tasks/search_by_building.json'
            ),
            (
                {'search': 'A'},
                '/tasks/search_by_level.json'
            ),
            (
                {'search': 'room'},
                '/tasks/search_by_area.json'
            ),
            (
                {'search': 'secon'},
                '/tasks/search_by_activity_name.json'
            ),
            (
                {'search': 'rth desc'},
                '/tasks/search_by_activity_task_description.json'
            ),
            (
                {'search': 'gan_gsta@gmail.com'},
                '/tasks/search_by_recipient_email.json'
            ),
            (
                {'search': 'soyer'},
                '/tasks/search_by_recipient_last_name.json'
            ),
            (
                {'search': 'joshua'},
                '/tasks/search_by_recipient_first_name.json'
            ),
            (
                {'sort': '-comment', 'expand': ['expanded_comment']},
                '/tasks/sort_by_comment_asc.json'
            ),
            (
                {'sort': 'comment', 'expand': ['expanded_comment']},
                '/tasks/sort_by_comment_desc.json'
            ),
            (
                {'expand': ['expanded_location_matrix.expanded_project']},
                '/tasks/search_with_project.json'
            ),
            (
                {'is_default_for_subtask': True},
                '/tasks/search_default_for_subtask.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-07-29T00:00:00', 'created_at__lte': '2020-07-29T23:59:59'},
                '/tasks/filter_by_created_at_range.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-07-29T00:00:00', 'updated_at__lte': '2020-07-29T23:59:59'},
                '/tasks/filter_by_updated_at_range.json'
            ),
            (
                {'sort': 'package_activity', 'distinct_by_package_activity_task_name': True},
                '/tasks/get_distinct_by_package_activity_task_name.json'
            ),
            (
                {'all': True, 'exclude_status': Task.Statuses.OUTSTANDING},
                '/tasks/filter_by_status_exclude.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        self._log_in_as_superuser()
        response = self.client.get('/api/projects/5/tasks/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        self._log_in_as_staff(project=5)
        response = self.client.get('/api/projects/5/tasks/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/tasks/', {'all': 1})

        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        superuser = self._get_superuser()
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        update_task = self.load_request_fixture('/tasks/update_task.json')

        self.force_login_user(superuser.pk)
        self.client.put('/api/projects/5/tasks/2/', update_task)
        self.client.put('/api/projects/5/tasks/2/', update_task)

        self.force_login_user(project_staff.pk)
        self.client.put('/api/projects/5/tasks/2/', {'status': 'outstanding'})

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Quality Report CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/tasks/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    def test_get_csv_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_client_csv_by_project_staff(self):
        url = reverse('tasks_generate_client_csv', kwargs={'project_pk': 5})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_client(project=5)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Quality Report CSV report for Client has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['stone.sour@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/tasks/client_csv_report_created.html'
            }
        ])

    def test_forbid_get_csv_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/csv/')

        self.assertForbidden(response)

    def test_unauthorized_get_csv(self):
        response = self.client.get('/api/projects/5/tasks/csv/')

        self.assertUnauthorized(response)

    @mock.patch('api.utilities.report_generators.TaskReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_superuser(self):
        superuser = self._get_superuser()
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        update_task = self.load_request_fixture('/tasks/update_task.json')

        self.force_login_user(superuser.pk)
        self.client.put('/api/projects/5/tasks/2/', update_task)
        self.client.put('/api/projects/5/tasks/2/', update_task)

        self.force_login_user(project_staff.pk)
        self.client.put('/api/projects/5/tasks/2/', {'status': 'outstanding'})

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/pdf/')

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Quality Report PDF report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/tasks/pdf_report_created.html'
            }
        ])

    @mock.patch('api.utilities.report_generators.TaskReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/pdf/')

        self.assertOk(response)


    @mock.patch('api.utilities.report_generators.TaskClientReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_superuser(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_client(project=5)
        response = self.client.get('/api/projects/5/tasks/client-pdf/')

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Quality Report PDF report for Client has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['stone.sour@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/tasks/client_pdf_report_created.html'
            }
        ])

    def test_forbid_get_pdf_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/pdf/')

        self.assertForbidden(response)

    def test_unauthorized_get_pdf(self):
        response = self.client.get('/api/projects/5/tasks/pdf/')

        self.assertUnauthorized(response)

    def test_search_by_client(self):
        self._log_in_as_client(project=5)
        url = reverse('tasks_list', kwargs={'project_pk': 5})
        response = self.client.get(url, {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/search_by_client.json')

    def test_search_by_consultant(self):
        self._log_in_as_consultant(project=5)
        url = reverse('tasks_list', kwargs={'project_pk': 5})
        response = self.client.get(url, {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/tasks/search_by_consultant.json')
