from django.db.models import Q

from api.models import Recipient
from api.tests.test import TestCase, data_provider


class RecipientTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/recipients.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_recipient = self.load_request_fixture('/recipients/new_recipient.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/recipients/', new_recipient)

        self.assertCreated(response)
        self.assertDatabaseHas(Recipient, new_recipient)
        self.assertEventsExist('/recipients/create_events_assertion.json')

    def test_unauthorized_create(self):
        new_recipient = self.load_request_fixture('/recipients/new_recipient.json')
        response = self.client.post('/api/recipients/', new_recipient)

        self.assertUnauthorized(response)

    def test_forbid_create_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)

        new_recipient = self.load_request_fixture('/recipients/new_recipient.json')
        response = self.client.post('/api/recipients/', new_recipient)

        self.assertForbidden(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/recipients/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/recipients/get_recipient.json')

    def test_forbid_get_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/recipients/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/recipients/1/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/recipients/1/')
        self.assertNoContent(response)
        self.assertSoftDeleted(Recipient, 1)
        self.assertEventsExist('/recipients/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/recipients/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/recipients/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_recipient = self.load_request_fixture('/recipients/update_recipient.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/recipients/1/', update_recipient)

        self.assertOk(response)
        self.assertDatabaseHas(Recipient, update_recipient)
        self.assertEventsExist('/recipients/update_events_assertion.json')

    def test_forbid_update_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        update_recipient = self.load_request_fixture('/recipients/update_recipient.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/recipients/1/', update_recipient)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_recipient = self.load_request_fixture('/recipients/update_recipient.json')
        response = self.client.put('/api/recipients/1/', update_recipient)

        self.assertUnauthorized(response)

    def get_task_update_filters(self):
        return (
            (
                {'building': ['Building A']},
                '/recipients/get_by_task_building.json'
            ),
            (
                {'area': ['Hall']},
                '/recipients/get_by_task_area.json'
            ),
            (
                {'level': ['A']},
                '/recipients/get_by_task_level.json'
            ),
            (
                {'package': [4]},
                '/recipients/get_by_task_package.json'
            ),
        )

    @data_provider(get_task_update_filters)
    def test_task_update_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/task-update/recipients/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_task_update_filters)
    def test_task_update_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/task-update/recipients/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_task_update_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/task-update/recipients/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_task_update_search(self):
        response = self.client.get('/api/projects/5/task-update/recipients/', {'all': 1})

        self.assertUnauthorized(response)

    def get_subtask_update_filters(self):
        return (
            (
                {'building': ['Building A']},
                '/recipients/get_by_subtask_building.json'
            ),
            (
                {'area': ['Hall']},
                '/recipients/get_by_subtask_area.json'
            ),
            (
                {'level': ['A']},
                '/recipients/get_by_subtask_level.json'
            ),
            (
                {'package': [4]},
                '/recipients/get_by_subtask_package.json'
            ),
            (
                {'task': [1]},
                '/recipients/get_by_subtask_task.json'
            ),
        )

    @data_provider(get_subtask_update_filters)
    def test_subtask_update_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtask-update/recipients/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_subtask_update_filters)
    def test_subtask_update_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtask-update/recipients/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_subtask_update_filters_for_subcontractor(self):
        return (
            (
                {'building': ['Building A']},
                '/recipients/get_by_subtask_building_by_subcontractor.json'
            ),
            (
                {'area': ['Hall']},
                '/recipients/get_by_subtask_area_by_subcontractor.json'
            ),
            (
                {'level': ['A']},
                '/recipients/get_by_subtask_level_by_subcontractor.json'
            ),
            (
                {'package': [4]},
                '/recipients/get_by_subtask_package_by_subcontractor.json'
            ),
            (
                {'task': [1]},
                '/recipients/get_by_subtask_task_by_subcontractor.json'
            ),
        )

    @data_provider(get_subtask_update_filters_for_subcontractor)
    def test_subtask_update_search_by_project_subcontractor(self, filters, fixture):
        project_staff = self._get_subcontractor(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtask-update/recipients/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_subtask_update_search_by_non_project_staff(self):
        project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtask-update/recipients/', {'all': 1})

        self.assertForbidden(response)

    def test_forbid_subtask_update_search_by_non_project_subcontractor(self):
        project_staff = self._get_subcontractor(~Q(project=5))
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtask-update/recipients/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_subtask_update_search(self):
        response = self.client.get('/api/projects/5/subtask-update/recipients/', {'all': 1})

        self.assertUnauthorized(response)

    def test_delete_with_m2m_reverse_relations(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/recipients/3/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Recipient, 3)
        self.assertEventsExist('/recipients/delete_with_m2m_reverse_relations_events_assertion.json')
