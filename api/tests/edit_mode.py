from django.db.models import Q

from api.models import EditMode, User
from api.tests.test import TestCase, data_provider


class EditModeTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/edit_mode.json']

    def test_create_by_project_staff(self):
        project_staff = self._get_staff(project=6)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/6/edit-mode/')

        self.assertCreated(response)
        self.assertDatabaseHas(EditMode, {'project': 6, 'user': 3})

    def test_create_for_entity_without_pointing_entity(self):
        project_staff = self._get_staff(project=6)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/6/edit-mode/', {'entity_id': 12})

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"entity":["Please specify entity to block."]}')

    def test_create_as_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/6/edit-mode/')

        self.assertCreated(response)
        self.assertDatabaseHas(EditMode, {'project': 6, 'user': superuser.pk})

    def test_forbid_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=4))
        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/4/edit-mode/')

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        response = self.client.post('/api/projects/4/edit-mode/')

        self.assertUnauthorized(response)

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/1/edit-mode/')

        self.assertNoContent(response)
        self.assertHardDeleted(EditMode, {'project': 1, 'user': 1})

    def test_forbid_delete_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=1))
        self.force_login_user(non_project_staff.pk)
        response = self.client.delete('/api/projects/1/edit-mode/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/1/edit-mode/')

        self.assertUnauthorized(response)

    def get_non_superusers(self):
        users = User.objects.filter(is_superuser=False, is_staff=True).order_by('groups__pk').\
            distinct('groups__pk').all()
        return [user.pk for user in users]

    @data_provider(get_non_superusers)
    def test_retrieve(self, user):
        self.force_login_user(user)
        response = self.client.get('/api/projects/2/edit-mode/', {
            'expand': 'expanded_user'
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/edit_mode/get_with_user.json')

    @data_provider(get_non_superusers)
    def test_retrieve_by_non_project_user(self, user):
        self.force_login_user(user)
        response = self.client.get('/api/projects/3/edit-mode/', {
            'expand': 'expanded_user'
        })

        self.assertForbidden(response)

    def test_retrieve_non_existing_edit_mode(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/6/edit-mode/')

        self.assertNoContent(response)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/3/edit-mode/', {
            'expand': 'expanded_user'
        })

        self.assertUnauthorized(response)
