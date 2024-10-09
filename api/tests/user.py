from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken

from api.mails.user.notify_company_admins_registration_user import NotifyCompanyAdminsRegistrationUser
from api.models import User, Company, ProjectUser, Recipient, Task, TaskUpdate, Subtask, SubtaskUpdate, QualityIssue, \
    QualityIssueUpdate, PackageHandoverDocumentMediaUpdate
from api.tests.test import TestCase, data_provider


class UserTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user.json']
    FROM_EMAIL = 'MBuild Support <some_email@email.com>'
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def mock_generate_token(self):
        return 123

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_user = self.load_request_fixture('/user/new_user.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertCreated(response)
        self.assertDatabaseHas(User, {'groups__in': [1], 'is_superuser': True, 'is_staff': True,
                                      'status': User.Status.APPROVED, 'email': new_user['email'],
                                      'first_name': new_user['first_name'], 'last_name': new_user['last_name']})
        self.assertDatabaseHas(ResetPasswordToken, {'user__email': new_user['email']})
        self.assertEmailEquals([
            {
                'subject': 'Your MBuild account has been created',
                'to': ['strong.man@gmail.com'],
                'from_email': self.FROM_EMAIL,
                'fixture': self.responses_fixtures_dir + '/user/set_password.html'
            }
        ])
        self.assertEventsExist('/user/create_events_assertion.json')

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_by_manager(self):
        new_user = self.load_request_fixture('/user/new_user.json')
        new_user['group'] = User.Group.ADMIN

        manager = self._get_user(groups=User.Group.MANAGER.value)
        self.force_login_user(manager.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertCreated(response)
        self.assertDatabaseHas(User, {'groups__in': [User.Group.ADMIN], 'is_staff': True, 'email': new_user['email'],
                                      'first_name': new_user['first_name'], 'last_name': new_user['last_name']})
        self.assertDatabaseHas(ResetPasswordToken, {'user__email': new_user['email'],
                                                    'user__first_name': new_user['first_name'],
                                                    'user__last_name': new_user['last_name']})
        self.assertEmailEquals([
            {
                'subject': 'Your MBuild account has been created',
                'to': ['strong.man@gmail.com'],
                'from_email': self.FROM_EMAIL,
                'fixture': self.responses_fixtures_dir + '/user/set_password.html'
            }
        ])
        self.assertEventsExist('/user/create_by_manager_events_assertion.json')

    def test_unauthorized_create(self):
        new_user = self.load_request_fixture('/user/new_user.json')
        response = self.client.post('/api/users/', new_user)

        self.assertUnauthorized(response)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_with_new_company(self):
        superuser = self._get_superuser()
        new_user = self.load_request_fixture('/user/new_user_with_new_company.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertCreated(response)
        self.assertDatabaseHas(Company, {'name': 'Maserati'})
        self.assertDatabaseHas(User, {'groups__in': [1], 'is_superuser': True, 'is_staff': True, 'company': 5,
                                      'status': User.Status.APPROVED, 'email': new_user['email']})

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_with_field_status(self):
        superuser = self._get_superuser()
        new_user = self.load_request_fixture('/user/new_user_status_rejected.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertCreated(response)
        self.assertDatabaseMissing(User, {'groups__in': [1], 'is_superuser': True, 'is_staff': True,
                                          'status': User.Status.REJECTED, 'email': new_user['email']})
        self.assertEventsExist('/user/create_with_field_status_events_assertion.json')

    def test_create_with_same_email_as_deleted(self):
        superuser = self._get_superuser()
        new_user = self.load_request_fixture('/user/new_user_with_same_email_as_deleted.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertConflict(response)

    def test_forbid_create_company_admin_by_non_company_admin(self):
        new_user = self.load_request_fixture('/user/new_user.json')
        new_user['group'] = User.Group.COMPANY_ADMIN.value

        non_company_admin = self._get_staff(~Q(groups=User.Group.COMPANY_ADMIN.value))
        self.force_login_user(non_company_admin.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertForbidden(response)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_with_non_existing_group(self):
        superuser = self._get_superuser()
        new_user = self.load_request_fixture('/user/new_user_with_non_existing_group.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/', new_user)

        self.assertBadRequest(response)

    def test_register(self):
        new_user = self.load_request_fixture('/user/register_user.json')

        response = self.client.post('/api/users/register/', new_user)

        self.assertCreated(response)
        self.assertIsNotNone(response.data)
        self.assertTrue('access' in response.data and 'refresh' in response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

        created_new_user = User.objects.order_by('-pk').first()
        self.assertTrue(created_new_user.project_set.filter(pk=3).exists())
        self.assertTrue(created_new_user.is_manager)
        self.assertEventsExist('/user/register_events_assertion.json')

        users_qs = User.objects.filter(company_id=created_new_user.company_id, deleted__isnull=True)
        self.assertEmailEquals([
            {
                'subject': NotifyCompanyAdminsRegistrationUser.subject,
                'to': [user.email for user in users_qs if user.is_company_admin and user.email],
                'from_email': self.FROM_EMAIL,
                'fixture': self.responses_fixtures_dir + '/user/notify_company_admins_registration_user.html'
            }
        ])

    def get_filters_for_user_search(self):
        return (
            (
                {'sort': 'company,id'},
                '/user/get_all_sorted_by_company.json'
            ),
            (
                {'sort': 'name,id'},
                '/user/get_all_sorted_by_name.json'
            ),
            (
                {'sort': 'group,id'},
                '/user/get_all_sorted_by_group.json'
            ),
            (
                {'page': 2, 'per_page': 2, 'sort': 'name,id'},
                '/user/get_per_page.json'
            ),
            (
                {'group': [1, 2], 'sort': 'name,id'},
                '/user/get_by_group.json'
            ),
            (
                {'search': ['wood'], 'sort': 'name,id'},
                '/user/get_by_search_query.json'
            ),
            (
                {'search': ['Seat'], 'sort': 'name,id'},
                '/user/search_by_company.json'
            ),
            (
                {'project_or_company_admins': 1, 'sort': 'name,id'},
                '/user/filter_by_project.json'
            ),
            (
                {'project': 1, 'expand': ['expanded_is_notifications_enabled', 'expanded_user_company']},
                '/user/filter_by_project_and_expand_is_notifications_enabled.json'
            ),
            (
                {'project__exclude': 1, 'sort': 'name,id'},
                '/user/exclude_by_project.json'
            ),
            (
                {'project__key_contacts__exclude_or_company_admins': 1, 'sort': 'name,id'},
                '/user/exclude_project_key_contacts.json'
            ),
            (
                {'status': ['rejected'], 'sort': 'name,id'},
                '/user/filter_by_status.json'
            ),
            (
                {'exclude_group': [1, 2], 'sort': 'name,id'},
                '/user/exclude_groups.json'
            ),
            (
                {'subcontractors_of_package_activity': 1, 'project': 1},
                '/user/filter_by_subcontractors_of_package_activity.json'
            ),
            (
                {'subcontractors_of_package_activity': 5, 'project': 1},
                '/user/filter_by_subcontractors_of_package_activity_with_default_result.json'
            ),
            (
                {'company': [1, 2]},
                '/user/filter_by_company.json'
            ),
            (
                {'subcontractors_company': 4},
                '/user/filter_subcontractors_by_company.json'
            ),
            (
                {'exclude_status': ['pending', 'rejected']},
                '/user/filter_by_exclude_status.json'
            ),
            (
                {'exclude_status': ['pending', 'rejected'], 'get_total_items_count': 1},
                '/user/get_total_items_count_for_filter_by_exclude_status.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/users/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_project_users_by_project_subcontractor(self):
        project_subcontractor = self._get_user(groups=User.Group.SUBCONTRACTOR.value, project=1)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 1, 'sort': 'name'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/user/search_by_project_subcontractor.json')

    def test_forbid_search_project_users_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_user(~Q(project=3), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 3, 'sort': 'name'})

        self.assertForbidden(response)

    def test_search_project_users_by_project_client(self):
        project_client = self._get_user(groups=User.Group.CLIENT.value, project=1)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 1, 'sort': 'name'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/user/search_by_project_client.json')

    def test_forbid_search_project_users_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=3), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 3, 'sort': 'name'})

        self.assertForbidden(response)

    def test_search_project_users_by_project_consultant(self):
        project_consultant = self._get_user(project=1, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 1, 'sort': 'name'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/user/search_by_project_consultant.json')

    def test_forbid_search_project_users_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=3), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/users/', {'project_or_company_admins': 3, 'sort': 'name'})

        self.assertForbidden(response)

    def test_get_all_forbidden_by_non_project_user(self):
        non_project_user = self._get_user(project__isnull=True)
        self.force_login_user(non_project_user.pk)
        response = self.client.get('/api/users/')

        self.assertForbidden(response)

    def test_unauthorized_get_all(self):
        response = self.client.get('/api/users/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        user_update = self.load_request_fixture('/user/update_user.json')
        user_update['group'] = User.Group.COMPANY_ADMIN

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/users/2/', user_update)

        self.assertOk(response)
        self.assertDatabaseHas(User, {'pk': 2, 'groups__in': [User.Group.COMPANY_ADMIN], 'is_superuser': True, 'is_staff': True,
                                      'company__in': [1], 'first_name': 'New Slim Shady'})

    def test_update_by_superuser_check_removed_projects(self):
        manager = self._get_manager()
        user_update = self.load_request_fixture('/user/update_user.json')
        user_update['group'] = User.Group.COMPANY_ADMIN

        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.put(f'/api/users/{manager.id}/', user_update)

        self.assertOk(response)
        self.assertEqual(ProjectUser.objects.filter(user_id=manager.id).count(), 0)

    def test_update_by_superuser_change_advantages(self):
        superuser = self._get_superuser()
        user_update = self.load_request_fixture('/user/update_user.json')
        user_update['group'] = User.Group.MANAGER

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/users/2/', user_update)

        self.assertOk(response)
        self.assertDatabaseHas(User, {'pk': 2, 'groups__in': [User.Group.MANAGER], 'is_superuser': False, 'is_staff': True,
                                      'company__in': [1], 'first_name': 'New Slim Shady'})

    def test_unauthorized_update(self):
        user_update = self.load_request_fixture('/user/update_user.json')
        user_update['group'] = 1
        response = self.client.put('/api/users/2/', user_update)

        self.assertUnauthorized(response)

    def test_update_self_profile(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user.json')

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertNoContent(response)
        self.assertDatabaseHas(User, {'pk': staff.pk, 'first_name': 'New Slim Shady'})

    def test_unauthorized_update_self_profile(self):
        user_update = self.load_request_fixture('/user/update_user.json')
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertUnauthorized(response)

    def test_forbid_update_self_role_to_company_admin(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/forbid_update_self_profile_role_to_company_admin.json')

        self.force_login_user(staff.pk)
        response = self.client.put('/api/users/2/', user_update)

        self.assertForbidden(response)

    def test_update_forbidden_for_non_staff(self):
        non_staff = self._get_user(is_superuser=False, is_staff=False)
        user_update = self.load_request_fixture('/user/update_user.json')

        self.force_login_user(non_staff.pk)
        response = self.client.put('/api/users/2/', user_update)

        self.assertForbidden(response)

    def test_forbid_company_admin_update_by_non_company_admin(self):
        non_company_admin = self._get_user(~Q(groups=User.Group.COMPANY_ADMIN.value))
        user_update = self.load_request_fixture('/user/update_user.json')

        self.force_login_user(non_company_admin.pk)
        response = self.client.put('/api/users/1/', user_update)

        self.assertForbidden(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/users/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(User, 2)
        # Check that related to user entities didn't delete.
        self.assertDatabaseHas(ProjectUser, {'user': 2})
        self.assertDatabaseHas(Recipient, {'user': 2})
        self.assertDatabaseHas(Task, {'user': 2})
        self.assertDatabaseHas(TaskUpdate, {'user': 2})
        self.assertDatabaseHas(Subtask, {'user': 2})
        self.assertDatabaseHas(SubtaskUpdate, {'user': 2})
        self.assertDatabaseHas(QualityIssue, {'user': 2})
        self.assertDatabaseHas(QualityIssueUpdate, {'user': 2})
        self.assertDatabaseHas(PackageHandoverDocumentMediaUpdate, {'user': 2})
        self.assertEventsExist('/user/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/users/2/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/users/2/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/users/2/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/user/get_user.json')

    def test_forbid_get_by_non_staff(self):
        non_staff = self._get_user(is_superuser=False, is_staff=False)
        self.force_login_user(non_staff.pk)
        response = self.client.get('/api/users/2/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/users/2/')

        self.assertUnauthorized(response)

    def test_get_self_profile(self):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get(reverse('profile-profile'))

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/user/get_user.json')

    def test_unauthorized_get_profile(self):
        response = self.client.get(reverse('profile-profile'))

        self.assertUnauthorized(response)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_password_reset(self):
        response = self.client.post('/api/password-reset/', {'email': 'cool.brad@gmail.com'})

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Reset your MBuild password',
                'from_email': self.FROM_EMAIL,
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/user/password_reset.html'
            }
        ])

    def test_update_password(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user_password.json')

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        updated_user = User.objects.get(pk=staff.pk)

        self.assertNoContent(response)
        self.assertEquals(updated_user.first_name, 'New Slim Shady')
        self.assertTrue(updated_user.check_password('123456Q#'))

    def test_update_password_without_new_password(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user_password.json')
        del user_update['new_password']

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertBadRequest(response)

    def test_update_password_without_password(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user_password.json')
        del user_update['password']

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertBadRequest(response)

    def test_update_password_with_invalid_password(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user_password.json')
        user_update['password'] = '235432dfsd'

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertBadRequest(response)

    def test_update_password_with_the_same_password(self):
        staff = self._get_staff()
        user_update = self.load_request_fixture('/user/update_user_password.json')
        user_update['new_password'] = '123456Qwe-'

        self.force_login_user(staff.pk)
        response = self.client.put(reverse('profile-profile'), user_update)

        self.assertBadRequest(response)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_restore_user_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/users/strong.bat@gmail.com/restore/')

        self.assertNoContent(response)
        self.assertDatabaseHas(User, {'email': 'strong.bat@gmail.com'})
        self.assertDatabaseHas(ResetPasswordToken, {'user__email': 'strong.bat@gmail.com'})
        self.assertEmailEquals([
            {
                'subject': 'Your MBuild account has been created',
                'to': ['strong.bat@gmail.com'],
                'from_email': self.FROM_EMAIL,
                'fixture': self.responses_fixtures_dir + '/user/set_password_to_restored_user.html'
            }
        ])
        self.assertEventsExist('/user/restore_user_events_assertion.json')

    def test_restore_user_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/users/strong.bat@gmail.com/restore/')

        self.assertForbidden(response)

    def test_unauthorized_restore_user(self):
        response = self.client.post('/api/users/strong.bat@gmail.com/restore/')

        self.assertUnauthorized(response)

    def test_approve_user_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)

        response = self.client.post('/api/users/11/approve/')

        self.assertNoContent(response)
        self.assertDatabaseHas(User, {'id': 11, 'status': User.Status.APPROVED})

    def test_approve_user_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/users/11/approve/')

        self.assertForbidden(response)

    def test_unauthorized_approve_user(self):
        response = self.client.post('/api/users/11/approve/')

        self.assertUnauthorized(response)

    def test_delete_own_account(self):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        token = self.get_user_token(staff)

        response = self.client.delete(reverse('profile-profile'), data={'refresh': str(token)})
        self.assertNoContent(response)

        user_delete_fields = {
            'id': staff.id,
            'first_name': 'Deleted',
            'last_name': 'Deleted',
            'is_staff': False,
            'is_superuser': False,
            'is_active': False,
            'email': None,
            'phone': None,
            'position': 'Deleted',
        }
        self.assertDatabaseHas(User, user_delete_fields)
        self.assertFalse(Recipient.objects.filter(user_id=staff.id).exists())

        response = self.client.delete(reverse('profile-profile'), data={'refresh': str(token)})
        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('user_generate_csv'))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'User CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/user/csv_report_created.html'
            }
        ])
