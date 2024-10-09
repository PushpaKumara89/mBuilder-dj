from django.db.models import Q

from api.models import PackageMatrixHiddenActivityTask, Task, Subtask, QualityIssue
from api.models.package_activity_task import PackageActivityTask
from api.tests.test import TestCase, data_provider


class PackageActivityTaskTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_activity_task.json']

    def test_create_by_superuser(self):
        new_package_activity_task = self.load_request_fixture('/package_activity_task/new_package_activity_task.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/package-activity-tasks/', new_package_activity_task)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageActivityTask, new_package_activity_task)
        self.assertEventsExist('/package_activity_task/create_events_assertion.json')

    def test_forbid_create_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        new_package_activity_task = self.load_request_fixture('/package_activity_task/new_package_activity_task.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/package-activity-tasks/', new_package_activity_task)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_activity_task = self.load_request_fixture('/package_activity_task/new_package_activity_task.json')
        response = self.client.post('/api/package-activity-tasks/', new_package_activity_task)

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        self._log_in_as_superuser()
        response = self.client.get('/api/package-activity-tasks/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity_task/get_package_activity_task.json')

    def test_forbid_get_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/package-activity-tasks/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/package-activity-tasks/1/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        self._log_in_as_superuser()
        response = self.client.delete('/api/package-activity-tasks/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(PackageActivityTask, 1)
        self.assertEventsExist('/package_activity_task/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/package-activity-tasks/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/package-activity-tasks/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        update_package_activity_task = self.load_request_fixture('/package_activity_task/update_package_activity_task.json')

        self._log_in_as_superuser()
        response = self.client.put('/api/package-activity-tasks/1/', update_package_activity_task)

        self.assertOk(response)
        self.assertDatabaseHas(PackageActivityTask, {**update_package_activity_task, 'pk': 1})
        self.assertEventsExist('/package_activity_task/update_events_assertion.json')

    def test_forbid_update_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        update_package_activity_task = self.load_request_fixture('/package_activity_task/update_package_activity_task.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/package-activity-tasks/1/', update_package_activity_task)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package_activity_task = self.load_request_fixture('/package_activity_task/update_package_activity_task.json')
        response = self.client.put('/api/package-activity-tasks/1/', update_package_activity_task)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True},
                '/package_activity_task/get_all.json'
            ),
            (
                {'sort': 'order'},
                '/package_activity_task/get_asc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_activity_task/get_page_per_page.json'
            ),
            (
                {'package_activity': [1, 2]},
                '/package_activity_task/get_by_package_activity.json'
            ),
            (
                {'is_default_for_subtask': True},
                '/package_activity_task/get_by_is_default_for_subtask.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        self._log_in_as_superuser()
        response = self.client.get('/api/package-activity-tasks/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/package-activity-tasks/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/package-activity-tasks/', {'all': 1})

        self.assertUnauthorized(response)

    def test_hide_by_project_staff(self):
        deleting_task_id = 1
        self._log_in_as_staff(project=5)
        response = self.client.post('/api/projects/5/package-matrix/3/activity-tasks/6/hide/')

        self.assertOk(response)
        self.assertDatabaseHas(PackageMatrixHiddenActivityTask, {'pk': 3, 'package_matrix': 3, 'package_activity_task': 6})
        self.assertSoftDeleted(Task, deleting_task_id)
        self.assertSoftDeleted(Subtask, {'task': deleting_task_id})
        self.assertSoftDeleted(QualityIssue, {'subtask__task': deleting_task_id})
        self.assertDatabaseHas(Task, 4)
        self.assertEventsExist('/package_activity_task/hide_task_events_assertion.json')

    def test_forbid_hide_for_staff_from_other_project(self):
        self._log_in_as_staff(~Q(project=5))
        response = self.client.post('/api/projects/5/package-matrix/3/activity-tasks/6/hide/')

        self.assertForbidden(response)

    def test_unauthorized_hide(self):
        response = self.client.post('/api/projects/5/package-matrix/3/activity-tasks/6/hide/')

        self.assertUnauthorized(response)

    def test_show_by_project_staff(self):
        restoring_task_id = 2
        self._log_in_as_staff(project=5)
        response = self.client.post('/api/projects/5/package-matrix/2/activity-tasks/5/show/')

        self.assertOk(response)
        self.assertDatabaseMissing(PackageMatrixHiddenActivityTask, {'pk': 1, 'package_matrix': 2,
                                                                     'package_activity_task': 5})
        # Make sure Task with related entities were restored.
        self.assertDatabaseHas(Task, restoring_task_id)
        self.assertDatabaseHas(Subtask, {'task': restoring_task_id})
        self.assertDatabaseHas(QualityIssue, {'subtask__task': restoring_task_id})

        # Make sure other entities were not restored.
        self.assertSoftDeleted(Task, 3)
        self.assertSoftDeleted(Subtask, 2)
        self.assertSoftDeleted(QualityIssue, 2)
        self.assertEventsExist('/package_activity_task/show_events_assertion.json')

    def test_hide_already_hidden(self):
        self._log_in_as_staff(project=5)
        response = self.client.post('/api/projects/5/package-matrix/2/activity-tasks/5/hide/')

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This package activity task already hidden."]}')

    def test_show_already_shown(self):
        self._log_in_as_staff(project=5)
        response = self.client.post('/api/projects/5/package-matrix/2/activity-tasks/2/show/')

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This package activity task already shown."]}')

    def test_forbid_show_by_staff_from_other_project(self):
        self._log_in_as_staff(~Q(project=5))
        response = self.client.post('/api/projects/5/package-matrix/2/activity-tasks/5/show/')

        self.assertForbidden(response)

    def test_unauthorized_show(self):
        self.force_login_user(4)
        response = self.client.post('/api/projects/5/package-matrix/2/activity-tasks/5/show/')

        self.assertForbidden(response)
