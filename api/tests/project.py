from unittest import mock

import pendulum
from django.core.files.storage import default_storage, FileSystemStorage
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from django.urls import reverse

from api.models import Media, Project, ProjectUser, Subtask, User, AssetRegister
from api.models.media_thumbnail import MediaThumbnail
from api.tests.test import TestCase, data_provider
from api.utilities.image_utilities import generate_image_name_by_size


class ProjectTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/projects.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def check_project_image_thumbnails(self, media):
        for sizes in MediaThumbnail.PROJECT_IMAGE_THUMBNAIL_SIZES:
            file_name = generate_image_name_by_size(media.link, sizes)

            file = default_storage.open(file_name)
            self.assertIsNotNone(file)

            default_storage.delete(file_name)

        default_storage.delete(media.link)

    def test_create(self):
        new_project = self.load_request_fixture('/project/new_project.json')
        media = Media.objects.get(pk=new_project['image_id'])
        default_storage.save(media.link, self.generate_fake_image())

        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/', new_project)

        self.assertCreated(response)
        self.assertDatabaseHas(Project, new_project)
        self.assertDatabaseHas(AssetRegister, {'project_id': response.data['id'], 'data': {}})
        self.check_project_image_thumbnails(media)
        self.assertEventsExist('/project/create_events_assertion.json')

    def test_unauthorized_create(self):
        new_project = self.load_request_fixture('/project/new_project.json')
        response = self.client.post('/api/projects/', new_project)

        self.assertUnauthorized(response)

    def test_forbid_create_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        new_project = self.load_request_fixture('/project/new_project.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/projects/', new_project)

        self.assertForbidden(response)

    def test_retrieve_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/get_project_by_superuser.json')

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertUnauthorized(response)

    def test_retrieve_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/get_project.json')

    def test_retrieve_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=1))
        self.force_login_user(other_project_staff.pk)
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertForbidden(response)

    def test_retrieve_as_project_client(self):
        project_client = self._get_user(project=1, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/get_project_as_client.json')

    def test_retrieve_as_client_from_other_project(self):
        other_project_client = self._get_user(~Q(project=1), groups=User.Group.CLIENT.value)
        self.force_login_user(other_project_client.pk)
        response = self.client.get('/api/projects/1/', {'expand': 'expanded_news'})

        self.assertForbidden(response)

    def test_retrieve_as_consultant_from_same_company_as_project_users(self):
        consultant = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=2)),
                                    groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/projects/2/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/retrieve_as_consultant_from_same_company_as_project_users.json')

    def test_forbid_retrieve_as_consultant_from_company_differ_than_project_users(self):
        consultant = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=3)),
                                    groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/projects/3/')

        self.assertForbidden(response)

    def test_retrieve_as_subcontractor_from_same_company_as_project_users(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=2)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/2/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/retrieve_as_subcontractor_from_same_company_as_project_users.json')

    def test_forbid_retrieve_as_subcontractor_from_company_differ_project_users(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=3)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/3/')

        self.assertForbidden(response)

    def test_delete_as_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Project, 1)
        self.assertEventsExist('/project/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/projects/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        # Test that related to the project subtasks marked as defects after project completion date update
        pendulum.set_test_now(pendulum.datetime(2020, 9, 30, 11, 00))

        update_project = self.load_request_fixture('/project/update_project.json')
        media = Media.objects.get(pk=update_project['image_id'])
        default_storage.save(media.link, self.generate_fake_image())

        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/', update_project)

        self.assertOk(response)
        self.assertDatabaseHas(Project, update_project)
        self.check_project_image_thumbnails(media)
        self.assertEventsExist('/project/update_events_assertion.json')
        # Check that is_defect field didn't change
        self.assertDatabaseHas(Subtask, {'pk': 1, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 2, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 3, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 4, 'is_defect': True})
        # Check that is_defect field changed
        self.assertDatabaseHas(Subtask, {'pk': 5, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 6, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 7, 'is_defect': True})
        self.assertSoftDeleted(Subtask, {'pk': 8, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 9, 'is_defect': True})
        self.assertDatabaseHas(Subtask, {'pk': 10, 'is_defect': True})

        pendulum.set_test_now(pendulum.datetime(2020, 2, 2))

    def test_update_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        update_project = self.load_request_fixture('/project/update_project.json')
        media = Media.objects.get(pk=update_project['image_id'])
        default_storage.save(media.link, self.generate_fake_image())

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/', update_project)

        self.assertOk(response)

    def test_forbid_update_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=5))
        update_project = self.load_request_fixture('/project/update_project.json')

        self.force_login_user(other_project_staff.pk)
        response = self.client.put('/api/projects/5/', update_project)

        self.assertForbidden(response)

    def test_update_with_marking_related_subtasks_as_not_defected(self):
        superuser = self._get_superuser()
        update_project = self.load_request_fixture('/project/update_project.json')
        update_project['completion_date'] = '2021-01-01'

        media = Media.objects.get(pk=update_project['image_id'])
        default_storage.save(media.link, self.generate_fake_image())

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/', update_project)

        self.assertOk(response)
        self.assertDatabaseHas(Project, update_project)
        self.check_project_image_thumbnails(media)
        # Check that is_defect field changed
        self.assertDatabaseHas(Subtask, {'pk': 1, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 2, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 3, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 4, 'is_defect': False})
        # Check that is_defect field didn't change
        self.assertDatabaseHas(Subtask, {'pk': 5, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 6, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 7, 'is_defect': False})
        self.assertSoftDeleted(Subtask, {'pk': 8, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 9, 'is_defect': False})
        self.assertDatabaseHas(Subtask, {'pk': 10, 'is_defect': False})

    def test_update_with_invalid_start_date(self):
        superuser = self._get_superuser()
        update_project = self.load_request_fixture('/project/update_invalid_project_start_date.json')
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/1/', update_project)

        self.assertBadRequest(response)

    def test_update_with_invalid_completion_date(self):
        superuser = self._get_superuser()
        update_project = self.load_request_fixture('/project/update_invalid_project_completion_date.json')
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/1/', update_project)

        self.assertBadRequest(response)

    def test_company_admin_update_quality_report_visible_for_clients(self):
        update_project = self.load_request_fixture('/project/company_admin_update_quality_report_visible_for_clients.json')
        self._log_in_as_company_admin()

        response = self.client.put('/api/projects/5/', update_project)
        self.assertOk(response)
        self.assertDatabaseHas(Project, update_project)

    def test_admin_forbid_update_quality_report_visible_for_clients(self):
        update_project = self.load_request_fixture('/project/company_admin_update_quality_report_visible_for_clients.json')
        self._log_in_as_admin()

        response = self.client.put('/api/projects/5/', update_project)
        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_project = self.load_request_fixture('/project/update_project.json')
        response = self.client.put('/api/projects/1/', update_project)

        self.assertUnauthorized(response)

    def get_filters_for_comany_admin_search(self):
        return (
            (
                {'all': True},
                '/project/get_all.json'
            ),
            (
                {'sort': '-name'},
                '/project/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/project/get_all_page_per_page.json'
            ),
            (
                {'status': ['tendering', 'under_construction']},
                '/project/get_by_status.json'
            ),
            (
                {'search': 'ect'},
                '/project/search_by_name.json'
            ),
            (
                {'search': 'eew'},
                '/project/search_by_number.json'
            )
        )

    @data_provider(get_filters_for_comany_admin_search)
    def test_search_by_company_admin(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def get_filters_for_project_manager_search(self):
        return (
            (
                {'all': True},
                '/project/get_all_by_project_manager.json'
            ),
            (
                {'sort': '-name'},
                '/project/get_all__by_project_manager_desc_order.json'
            ),
            (
                {'page': 1, 'per_page': 1},
                '/project/get_all_page_per_page_by_project_manager.json'
            ),
            (
                {'status': ['tendering', 'under_construction']},
                '/project/get_by_status_by_project_manager.json'
            ),
            (
                {'search': 'ect'},
                '/project/search_by_name_by_project_manager.json'
            ),
            (
                {'search': '6uy'},
                '/project/search_by_number_by_project_manager.json'
            )
        )

    @data_provider(get_filters_for_project_manager_search)
    def test_search_by_project_manager(self, filters, fixture):
        manager = self._get_staff(groups=User.Group.MANAGER.value)
        self.force_login_user(manager.pk)
        response = self.client.get('/api/projects/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_as_client(self):
        client = self._get_user(groups=User.Group.CLIENT.value)
        self.force_login_user(client.pk)
        response = self.client.get('/api/projects/', {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/search_as_client.json')

    def test_search_as_admin(self):
        self._log_in_as_admin()
        response = self.client.get('/api/projects/', {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/search_as_admin.json')

    def test_add_users_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/users/add/', {'users': [11, 12]})

        self.assertOk(response)
        self.assertDatabaseHas(Project, {'users__pk': 11, 'pk': 1})
        self.assertDatabaseHas(Project, {'users__pk': 12, 'pk': 1})
        self.assertEventsExist('/project/add_users_events_assertion.json')

    def test_forbid_add_users_by_staff_from_other_project(self):
        other_project_staff = self._get_staff(~Q(project=1))
        self.force_login_user(other_project_staff.pk)
        response = self.client.post('/api/projects/1/users/add/', {'users': [11, 12]})

        self.assertForbidden(response)

    def test_disable_add_users_if_satatus_pending(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/1/users/add/', {'users': [1]})

        self.assertEquals(response.status_code, 400)

    def test_add_users_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/1/users/add/', {'users': [11, 12]})

        self.assertOk(response)
        self.assertDatabaseHas(Project, {'users__pk': 11, 'pk': 1})
        self.assertDatabaseHas(Project, {'users__pk': 12, 'pk': 1})
        self.assertEventsExist('/project/add_users_by_company_admin_events_assertion.json')

    def test_update_user_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/1/users/2/', {'is_notifications_enabled': True})

        self.assertNoContent(response)
        self.assertDatabaseHas(ProjectUser, {'user': 2, 'is_notifications_enabled': True})
        self.assertEventsExist('/project/update_user_by_company_admin_events_assertion.json')

    def test_forbid_update_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/projects/1/users/2/', {'is_notifications_enabled': True})

        self.assertForbidden(response)

    def test_unauthorized_user_update(self):
        response = self.client.put('/api/projects/1/users/2/', {'is_notifications_enabled': True})

        self.assertUnauthorized(response)

    def test_remove_himself_by_manager(self):
        project_manager = self._get_user(project=1, groups=User.Group.MANAGER.value)
        self.force_login_user(project_manager.pk)
        response = self.client.post('/api/projects/1/users/remove/', {'users': [project_manager.pk]})

        self.assertOk(response)
        self.assertEventsExist('/project/remove_himself_by_manager_events_assertion.json')

    def test_forbid_remove_users_by_manager_from_other_project(self):
        project_manager = self._get_user(~Q(project=1), groups=User.Group.MANAGER.value)
        self.force_login_user(project_manager.pk)
        response = self.client.post('/api/projects/1/users/remove/', {'users': [2]})

        self.assertForbidden(response)

    def test_remove_users_by_admin(self):
        admin = self._get_staff(project=2, groups=User.Group.ADMIN.value)
        self.force_login_user(admin.pk)
        response = self.client.post('/api/projects/2/users/remove/', {'users': [2, 3]})

        self.assertOk(response)
        self.assertDatabaseMissing(Project, {'users__pk': 2, 'pk': 2})
        self.assertDatabaseMissing(Project, {'users__pk': 3, 'pk': 2})
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 2, 'pk': 2})
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 3, 'pk': 2})
        self.assertEventsExist('/project/remove_users_by_admin_events_assertion.json')

    def test_forbid_remove_users_by_non_project_admin(self):
        admin = self._get_staff(~Q(project=4), groups=User.Group.ADMIN.value)
        self.force_login_user(admin.pk)
        response = self.client.post('/api/projects/4/users/remove/', {'users': [3]})

        self.assertForbidden(response)

    def test_unauthorized_remove_users(self):
        response = self.client.post('/api/projects/4/users/remove/', {'users': [3]})

        self.assertUnauthorized(response)

    def test_forbid_remove_client_with_active_quality_issues(self):
        admin = self._get_staff(project=2, groups=User.Group.ADMIN.value)
        self.force_login_user(admin.pk)
        response = self.client.post('/api/projects/2/users/remove/', {'users': [5, 6]})

        self.assertBadRequest(response)
        self.assertEquals(response.data,
                          {'users': ['You cannot remove client cool.client@gmail.com with active quality issues.']})

    def test_remove_users_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/2/users/remove/', {'users': [2, 3]})

        self.assertOk(response)
        self.assertDatabaseMissing(Project, {'users__pk': 2, 'pk': 2})
        self.assertDatabaseMissing(Project, {'users__pk': 3, 'pk': 2})
        self.assertEventsExist('/project/remove_users_by_company_admin_events_assertion.json')

    def test_add_key_contacts_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/key-contacts/add/', {'key_contacts': [1, 3]})

        self.assertOk(response)
        self.assertDatabaseHas(Project, {'key_contacts__pk': 1, 'pk': 1})
        self.assertDatabaseHas(Project, {'key_contacts__pk': 3, 'pk': 1})
        self.assertEventsExist('/project/add_key_contacts_events_assertion.json')

    def test_add_key_contacts_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/1/key-contacts/add/', {'key_contacts': [1, 3]})

        self.assertOk(response)
        self.assertDatabaseHas(Project, {'key_contacts__pk': 1, 'pk': 1})
        self.assertDatabaseHas(Project, {'key_contacts__pk': 3, 'pk': 1})
        self.assertEventsExist('/project/add_key_contacts_by_company_admin_events_assertion.json')

    def test_forbid_add_key_contacts_by_staff_from_other_project(self):
        non_project_staff = self._get_staff(~Q(project=3))
        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/3/key-contacts/add/', {'key_contacts': [1, 3]})

        self.assertForbidden(response)

    def test_unauthorized_add_key_contacts(self):
        response = self.client.post('/api/projects/3/key-contacts/add/', {'key_contacts': [1, 3]})

        self.assertUnauthorized(response)

    def test_remove_key_contacts_by_project_staff(self):
        project_staff = self._get_staff(project=2)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/2/key-contacts/remove/', {'key_contacts': [2, 3]})

        self.assertOk(response)
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 2, 'pk': 2})
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 3, 'pk': 2})
        self.assertEventsExist('/project/remove_key_contacts_by_admin_events_assertion.json')

    def test_forbid_remove_key_contacts_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=4))
        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/4/key-contacts/remove/', {'key_contacts': [3]})

        self.assertForbidden(response)

    def test_remove_key_contacts_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/2/key-contacts/remove/', {'key_contacts': [2, 3]})

        self.assertOk(response)
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 2, 'pk': 2})
        self.assertDatabaseMissing(Project, {'key_contacts__pk': 3, 'pk': 2})
        self.assertEventsExist('/project/remove_key_contacts_by_company_admin_events_assertion.json')

    def test_unauthorized_remove_key_contacts(self):
        response = self.client.post('/api/projects/2/key-contacts/remove/', {'key_contacts': [2, 3]})

        self.assertUnauthorized(response)

    def test_list_by_consultant(self):
        consultant = self._get_user(groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/projects/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/project/list_projects_by_consultant.json')

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('project_generate_csv'))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Project CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/project/csv_report_created.html'
            }
        ])
