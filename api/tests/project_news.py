from django.db.models import Q

from api.models.project_news import ProjectNews
from api.tests.test import TestCase, data_provider


class ProjectNewsTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/project_news.json']

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_project_news = self.load_request_fixture('/project_news/new_project_news.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/project-news/', new_project_news)

        self.assertCreated(response)
        self.assertDatabaseHas(ProjectNews, new_project_news)
        self.assertEventsExist('/project_news/create_events_assertion.json')

    def test_create_by_project_user(self):
        project_user = self._get_user(is_superuser=False, project=2)
        self.force_login_user(project_user.pk)

        new_project_news = self.load_request_fixture('/project_news/new_project_news_by_project_user.json')
        response = self.client.post('/api/project-news/', new_project_news)

        self.assertCreated(response)
        self.assertDatabaseHas(ProjectNews, new_project_news)

    def test_create_by_user_from_other_project(self):
        project_user = self._get_user(~Q(project=2), is_superuser=False)
        self.force_login_user(project_user.pk)

        new_project_news = self.load_request_fixture('/project_news/new_project_news_by_project_user.json')
        response = self.client.post('/api/project-news/', new_project_news)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_project_news = self.load_request_fixture('/project_news/new_project_news_by_project_user.json')
        response = self.client.post('/api/project-news/', new_project_news)

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/project-news/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project_news/get_news_by_company_admin.json')

    def test_get_by_project_user(self):
        project_user = self._get_user(project=2, is_superuser=False)
        self.force_login_user(project_user.pk)
        response = self.client.get('/api/project-news/5/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project_news/get_news_by_project_manager.json')

    def test_get_by_user_from_other_project(self):
        other_project_user = self._get_user(~Q(project=2), is_superuser=False)
        self.force_login_user(other_project_user.pk)
        response = self.client.get('/api/project-news/5/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/project-news/5/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/project-news/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(ProjectNews, 1)
        self.assertEventsExist('/project_news/delete_events_assertion.json')

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project=2)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/project-news/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(ProjectNews, 1)

    def test_forbid_delete_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=2))
        self.force_login_user(other_project_staff.pk)
        response = self.client.delete('/api/media/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/media/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_project_news = self.load_request_fixture('/project_news/update_project_news.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/project-news/1/', update_project_news)

        self.assertOk(response)
        self.assertDatabaseHas(ProjectNews, update_project_news)
        self.assertEventsExist('/project_news/update_events_assertion.json')

    def test_update_by_project_staff(self):
        project_staff = self._get_staff(project=2)
        update_project_news = self.load_request_fixture('/project_news/update_project_news.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/project-news/1/', update_project_news)

        self.assertOk(response)
        self.assertDatabaseHas(ProjectNews, update_project_news)

    def test_update_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=2))
        update_project_news = self.load_request_fixture('/project_news/update_project_news.json')

        self.force_login_user(other_project_staff.pk)
        response = self.client.put('/api/project-news/1/', update_project_news)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_project_news = self.load_request_fixture('/project_news/update_project_news.json')
        response = self.client.put('/api/project-news/1/', update_project_news)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True},
                '/project_news/get_all.json'
            ),
            (
                {'sort': '-title'},
                '/project_news/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/project_news/get_all_page_per_page.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/project-news/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_staff(self, filters, fixture):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/project-news/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_search(self):
        response = self.client.get('/api/project-news/', {'all': 1})

        self.assertUnauthorized(response)
