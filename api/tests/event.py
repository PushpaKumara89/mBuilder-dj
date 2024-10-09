from django.db.models import Q

from api.tests.test import TestCase


class EventTest(TestCase):
    mongo_fixtures = ['api/tests/fixtures/dumps/mongo/event.json']
    fixtures = ['api/tests/fixtures/dumps/event.json']

    def test_staff_list(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/events/', {'processed_from': '2020-02-02'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/event/staff_get_processed_from.json')

    def test_list_via_api_key(self):
        response = self.client.get('/api/projects/1/events/', {'processed_from': '2020-02-02'},
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/event/staff_get_processed_from.json')

    def test_create_by_staff(self):
        data = self.load_request_fixture('/events/create_events.json')
        project_staff = self._get_staff(project=1)

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/events/', data)

        self.assertCreated(response)
        self.__remove_id_from_response_data(response)
        self.assertEqualsFixture(response.data, '/event/create_events_assertion.json')

    def test_create_by_superuser(self):
        data = self.load_request_fixture('/events/create_events.json')
        project_staff = self._get_superuser()

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/events/', data)

        self.assertCreated(response)
        self.__remove_id_from_response_data(response)
        self.assertEqualsFixture(response.data, '/event/create_events_assertion.json')

    def test_unauthorized_create(self):
        data = self.load_request_fixture('/events/create_events.json')
        response = self.client.post('/api/projects/1/events/', data)

        self.assertUnauthorized(response)

    def test_unauthorized_list(self):
        response = self.client.get('/api/projects/1/events/', {'processed_from': '2020-02-02'})

        self.assertUnauthorized(response)

    def test_super_admin_list(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/1/events/', {'processed_from': '2020-02-02'})

        self.assertEqualsFixture(response.data, '/event/super_admin_get_processed_from.json')

    def test_forbid_list(self):
        non_project_staff = self._get_staff(~Q(project=1))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/1/events/', {'processed_from': '2020-02-02'})

        self.assertForbidden(response)

    def __remove_id_from_response_data(self, response):
        for key, r in enumerate(response.data):
            del response.data[key]['id']
