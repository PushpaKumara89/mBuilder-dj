from django.db.models import Q

from api.models import TaskUpdate, Task, Recipient
from api.tests.test import TestCase, data_provider


class TaskUpdateTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/tasks_updates.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        del new_task_update['files']
        recipients = new_task_update.pop('recipients')

        self.assertCreated(response)
        self.assertDatabaseHas(TaskUpdate, new_task_update)
        self.assertDatabaseHas(Task, {'pk': 1, 'status': new_task_update['new_data']['status'], 'user__pk': 1})

        for recipient in recipients:
            self.assertDatabaseHas(Recipient, recipient)

        self.assertIsNotNone(Task.objects.get(pk=1).date_of_approval)
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/task_accepted_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/task_accepted_recipients.html'
            }
        ])
        self.assertEventsExist('/task_update/create_events_assertion.json')

    def test_create_by_superuser_without_recipients(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update_without_recipients.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/4/updates/', new_task_update)

        self.assertCreated(response)

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Quality Critical Task Statused – Project 5, Building A - A - Meeting room',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/task_part_complete_multiplex_without_recipients.html'
            }
        ])

    def test_create_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertCreated(response)

    def test_forbid_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update.json')
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertUnauthorized(response)

    def test_bulk_create_by_superuser(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_bulk_task_update.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/updates/', new_task_update)

        recipients = new_task_update.pop('recipients')

        self.assertNoContent(response)
        self.assertDatabaseHas(TaskUpdate, {'task': 1, 'new_data': {'status': 'accepted'}, 'old_data': {'status': 'not_applicable'}})
        self.assertDatabaseHas(TaskUpdate, {'task': 2, 'new_data': {'status': 'accepted'}, 'old_data': {'status': 'not_applicable'}})
        self.assertDatabaseHas(TaskUpdate, {'task': 3, 'new_data': {'status': 'accepted'}, 'old_data': {'status': 'not_verified'}})
        self.assertDatabaseHas(Task, {'pk': 1, 'status': 'accepted', 'user__pk': 1})
        self.assertDatabaseHas(Task, {'pk': 2, 'status': 'accepted', 'user__pk': 1})
        self.assertDatabaseHas(Task, {'pk': 3, 'status': 'accepted', 'user__pk': 1})

        for recipient in recipients:
            self.assertDatabaseHas(Recipient, recipient)

        self.assertIsNotNone(Task.objects.get(pk=1).date_of_approval)
        self.assertIsNotNone(Task.objects.get(pk=2).date_of_approval)
        self.assertIsNotNone(Task.objects.get(pk=3).date_of_approval)
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_first_task_accepted_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_first_task_accepted_recipients.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_second_task_accepted_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_second_task_accepted_recipients.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_third_task_accepted_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/bulk_create_third_task_accepted_recipients.html'
            }
        ])
        self.assertEventsExist('/task_update/bulk_create_events_assertion.json')

    def test_bulk_create_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        new_task_update = self.load_request_fixture('/tasks_updates/new_bulk_task_update.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/tasks/updates/', new_task_update)

        self.assertNoContent(response)

    def test_forbid_bulk_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        new_task_update = self.load_request_fixture('/tasks_updates/new_bulk_task_update.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/tasks/updates/', new_task_update)

        self.assertForbidden(response)

    def test_unauthorized_bulk_create(self):
        new_task_update = self.load_request_fixture('/tasks_updates/new_bulk_task_update.json')
        response = self.client.post('/api/projects/5/tasks/updates/', new_task_update)

        self.assertUnauthorized(response)

    def test_create_part_completed(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/part_complete_task_update.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        del new_task_update['files']
        recipients = new_task_update.pop('recipients')

        self.assertCreated(response)
        self.assertDatabaseHas(TaskUpdate, new_task_update)
        self.assertDatabaseHas(Task, {'pk': 1, 'status': new_task_update['new_data']['status'], 'user__pk': 1})

        for recipient in recipients:
            self.assertDatabaseHas(Recipient, recipient)

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/task_part_completed_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/task_update/task_part_completed_recipients.html'
            }
        ])
        self.assertEventsExist('/task_update/create_part_completed_events_assertion.json')

    def test_create_with_files(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update_with_files.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertCreated(response)
        task_update = TaskUpdate.objects.filter(pk=response.data['id']).get()
        self.assertTrue(task_update.files.filter(pk__in=[1, 2]).exists())
        self.assertEventsExist('/task_update/create_with_files_events_assertion.json')

    def test_create_incorrect_new_data(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update_incorrect_new_data.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertBadRequest(response)

    def test_create_incorrect_new_data_incorrect_field(self):
        superuser = self._get_superuser()
        new_task_update = self.load_request_fixture('/tasks_updates/new_task_update_incorrect_new_data_incorrect_field.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/tasks/1/updates/', new_task_update)

        self.assertBadRequest(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/task_update/get_task_update.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/task_update/get_task_update.json')

    def test_forbid_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/tasks/1/updates/1/')

        self.assertUnauthorized(response)

    def test_get_with_expandable_fields(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/1/', {'expand': ['expanded_task.expanded_package', 'expanded_user', 'expanded_files']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/task_update/get_task_update_with_expandable_fields.json')

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/tasks/1/updates/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(TaskUpdate, 1)
        self.assertEventsExist('/task_update/delete_events_assertion.json')

    def test_forbid_delete_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/tasks/1/updates/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/tasks/1/updates/1/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'created_at'},
                '/task_update/get_all_sorted_by_created_at.json'
            ),
            (
                {'all': True, 'sort': '-created_at'},
                '/task_update/get_all_sorted_by_created_at_desc.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/tasks/1/updates/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/tasks/1/updates/', {'all': 1})

        self.assertUnauthorized(response)
