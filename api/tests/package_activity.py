from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from rest_framework.reverse import reverse

from api.models import PackageActivityTask, PackageMatrixHiddenActivityTask, Task, User, ProjectUser
from api.models.package_activity import PackageActivity
from api.tests.test import TestCase, data_provider


class PackageActivityTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_activity.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_package_activity = self.load_request_fixture('/package_activity/new_package_activity.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/package-activities/', new_package_activity)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/package_activity/create_new_package_activity.json')
        self.assertDatabaseHas(PackageActivity, {'name': 'New package activity', 'activity_id': 'sdfugh#456',
                                                 'description': new_package_activity['description'],
                                                 'description_image_id': new_package_activity['description_image'],
                                                 'files__pk__in': new_package_activity['files']})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 5, 'package_activity__activity_id': 'sdfugh#456'})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 6, 'package_activity__activity_id': 'sdfugh#456'})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 7, 'package_activity__activity_id': 'sdfugh#456'})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 8, 'package_activity__activity_id': 'sdfugh#456'})
        self.assertEventsExist('/package_activity/create_events_assertion.json')

    def test_create_with_duplicated_task_description_by_superuser(self):
        superuser = self._get_superuser()
        new_package_activity = self.load_request_fixture('/package_activity/new_package_activity_with_duplicated_task_description.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/package-activities/', new_package_activity)

        self.assertBadRequest(response)

    def test_forbid_create_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        new_package_activity = self.load_request_fixture('/package_activity/new_package_activity.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.post('/api/package-activities/', new_package_activity)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_package_activity = self.load_request_fixture('/package_activity/new_package_activity.json')
        response = self.client.post('/api/package-activities/', new_package_activity)

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/package-activities/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_package_activity.json')

    def test_forbid_get_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.get('/api/package-activities/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/package-activities/1/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/package-activities/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(PackageActivity, 1)
        self.assertEventsExist('/package_activity/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/package-activities/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/package-activities/1/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_package_activity = self.load_request_fixture('/package_activity/update_package_activity.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/package-activities/1/', update_package_activity)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/update_package_activity.json')
        self.assertDatabaseHas(PackageActivity, {'name': 'Updated package activity', 'pk': 1, 'files__pk__in': update_package_activity['files']})
        self.assertDatabaseHas(PackageActivityTask, {'description': 'New description', 'order': 1, 'pk': 1, 'package_activity': 1})
        self.assertSoftDeleted(PackageActivityTask, 4)
        self.assertSoftDeleted(Task, 1)
        self.assertHardDeleted(Task, 2)
        self.assertDatabaseHas(PackageActivityTask, {'pk': 2, 'is_default_for_subtask': False})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 3, 'package_activity': 2})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 9, 'package_activity': 1, **update_package_activity['package_activity_tasks'][2]})
        self.assertDatabaseHas(PackageMatrixHiddenActivityTask, 1)
        self.assertDatabaseHas(PackageMatrixHiddenActivityTask, 2)
        self.assertDatabaseHas(PackageMatrixHiddenActivityTask, 3)
        self.assertDatabaseHas(PackageMatrixHiddenActivityTask, 4)
        self.assertEventsExist('/package_activity/update_events_assertion.json')

    def test_update_with_changed_default_for_subtask_by_superuser(self):
        superuser = self._get_superuser()
        update_package_activity = self.load_request_fixture('/package_activity/update_package_activity_with_changed_default_for_subtask.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/package-activities/1/', update_package_activity)

        self.assertOk(response)
        self.assertDatabaseMissing(PackageActivityTask, {'pk': 2, 'is_default_for_subtask': True})
        self.assertDatabaseHas(PackageActivityTask, {'package_activity': 1, 'is_default_for_subtask': True,
                                                     'description': 'My description'})

    def test_update_task_with_same_description_by_superuser(self):
        superuser = self._get_superuser()
        update_package_activity = self.load_request_fixture('/package_activity/update_package_activity_task_with_same_description.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/package-activities/1/', update_package_activity)

        self.assertOk(response)
        self.assertDatabaseHas(PackageActivity, {'name': 'Updated package activity', 'pk': 1})
        self.assertDatabaseHas(PackageActivityTask, {'description': "First desc", 'order': 1, 'pk': 1, 'package_activity': 1})
        self.assertSoftDeleted(PackageActivityTask, 2)
        self.assertDatabaseHas(PackageActivityTask, {'pk': 3, 'package_activity': 2})
        self.assertDatabaseHas(PackageActivityTask, {'pk': 10, 'package_activity': 1, **update_package_activity['package_activity_tasks'][1]})
        self.assertEventsExist('/package_activity/update_with_same_description_events_assertion.json')

    def test_forbid_update_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        update_package_activity = self.load_request_fixture('/package_activity/update_package_activity.json')

        self.force_login_user(non_superuser.pk)
        response = self.client.put('/api/package-activities/1/', update_package_activity)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_package_activity = self.load_request_fixture('/package_activity/update_package_activity.json')
        response = self.client.put('/api/package-activities/1/', update_package_activity)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'expand': ['expanded_projects_count', 'expanded_files', 'expanded_files_count', 'expanded_description',
                                         'expanded_description_image']},
                '/package_activity/get_all.json'
            ),
            (
                {'sort': '-name'},
                '/package_activity/get_all_desc_order.json'
            ),
            (
                {'sort': '-tasks_count'},
                '/package_activity/get_ordered_by_tasks_count_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/package_activity/get_all_page_per_page.json'
            ),
            (
                {'search': 'ird'},
                '/package_activity/search.json'
            ),
            (
                {'exclude_bound_with_project': 5},
                '/package_activity/get_all_excluded_for_project.json',
            ),
            (
                {'package': [3, 4]},
                '/package_activity/get_by_package.json'
            ),
            (
                {'project': [5], 'has_published_tasks': True},
                '/package_activity/get_by_project.json'
            ),
            (
                {'building': ['Building A']},
                '/package_activity/get_by_building.json'
            ),
            (
                {'level': ['A']},
                '/package_activity/get_by_level.json'
            ),
            (
                {'area': ['Hall']},
                '/package_activity/get_by_area.json'
            ),
            (
                {'package_handover_document_type': [1], 'project': [5]},
                '/package_activity/get_filtered_by_document_type.json'
            ),
            (
                {'asset_handover_document_company': [2], 'project': [5]},
                '/package_activity/get_filter_by_asset_handover_document_company.json'
            ),
            (
                {'id': [1, 2, 3]},
                '/package_activity/get_filtered_by_ids.json'
            ),
            (
                {'package_handover_document_company': [1]},
                '/package_activity/get_filtered_by_package_handover_document_company.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/package-activities/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_staff(self, filters, fixture):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/package-activities/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_subcontractor(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/package-activities/', {'project': [5], 'has_published_tasks': True, 'filter_by_company': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/search_by_subcontractor.json')

    def test_search_by_subcontractor_with_invalid_parameter_value(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/package-activities/', {'project': [5], 'has_published_tasks': True, 'filter_by_company': 12})

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"filter_by_company":"Parameter should be a boolean."}')

    def test_search_by_consultant(self):
        consultant = self._get_consultant(project=5)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/package-activities/', {'project': [5], 'has_published_tasks': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/search_by_consultant.json')

    def test_search_by_client(self):
        client = self._get_user(groups=User.Group.CLIENT.value, project=5)
        self.force_login_user(client.pk)
        response = self.client.get('/api/package-activities/', {'project': [5], 'has_published_tasks': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/search_by_client.json')

    def test_forbid_search_by_subcontractor(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(project=6,
                                                                          user__company=OuterRef('company'))),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/package-activities/', {'project': [6], 'has_published_tasks': True})

        self.assertForbidden(response)

    def test_forbid_search_by_consultant(self):
        consultant = self._get_user(~Exists(ProjectUser.objects.filter(project=6, user__company=OuterRef('company'))),
                                    groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/package-activities/', {'project': [6], 'has_published_tasks': True})

        self.assertForbidden(response)

    def test_forbid_search_by_client(self):
        client = self._get_user(~Q(project=6), groups=User.Group.CLIENT.value)
        self.force_login_user(client.pk)
        response = self.client.get('/api/package-activities/', {'project': [6], 'has_published_tasks': True})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/package-activities/', {'project': [6], 'has_published_tasks': True})

        self.assertUnauthorized(response)

    def test_get_for_matrix_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-activities/2/', {'expand': ['expanded_package_activity_tasks.expanded_hidden']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_matrix.json')

    def test_get_for_matrix_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-activities/2/', {'expand': ['expanded_package_activity_tasks.expanded_hidden']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_matrix.json')

    def test_get_for_matrix_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/package-activities/2/', {'expand': ['expanded_package_activity_tasks.expanded_hidden']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_matrix.json')

    def test_forbid_get_for_matrix_by_staff_outside_project(self):
        staff_outside_project = self._get_staff(~Q(project=5))
        self.force_login_user(staff_outside_project.pk)
        response = self.client.get('/api/projects/5/package-activities/2/')

        self.assertForbidden(response)

    def test_forbid_get_for_matrix_by_client_not_from_project(self):
        client_not_from_project = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        self.force_login_user(client_not_from_project.pk)
        response = self.client.get('/api/projects/5/package-activities/2/')

        self.assertForbidden(response)

    def test_forbid_get_for_matrix_by_consultant_without_project_users_from_same_company(self):
        consultant = self._get_user(~Exists(ProjectUser.objects.filter(project=5, user__company=OuterRef('company'))),
                                    groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/projects/5/package-activities/2/')

        self.assertForbidden(response)

    def test_forbid_get_for_matrix_by_subcontractor_without_project_users_from_same_company(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(project=5,
                                                                          user__company=OuterRef('company'))),
                                       groups=User.Group.CONSULTANT.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/package-activities/2/')

        self.assertForbidden(response)

    def test_unauthorized_get_for_matrix(self):
        response = self.client.get('/api/projects/5/package-activities/2/')

        self.assertUnauthorized(response)

    def test_get_difficult_case_for_project_package_matrix(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)

        response = self.client.get('/api/package-activities/', {'exclude_bound_with_project': 7})
        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_difficult_case_first_response.json')

        response = self.client.post('/api/projects/7/package-matrix/', {'package': 3, 'package_activity': [5]})
        self.assertCreated(response)

        response = self.client.get('/api/package-activities/', {'exclude_bound_with_project': 7})
        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_difficult_case_second_response.json')

        response = self.client.delete('/api/package-matrix/8/')
        self.assertNoContent(response)

        response = self.client.get('/api/package-activities/', {'exclude_bound_with_project': 7})
        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_difficult_case_third_response.json')

    def test_search_for_package_matrix_by_staff(self):
        staff = self._get_staff()
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_package_matrix.json')

    def test_search_for_package_matrix_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_package_matrix.json')

    def test_search_for_package_matrix_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_for_package_matrix.json')

    def test_forbid_search_for_package_matrix_by_subcontractor_without_project_users_from_same_company(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(project=5,
                                                                          user__company=OuterRef('company'))),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertForbidden(response)

    def test_forbid_search_for_package_matrix_by_consultant_without_project_users_from_same_company(self):
        consultant = self._get_user(~Exists(ProjectUser.objects.filter(project=5, user__company=OuterRef('company'))),
                                    groups=User.Group.CONSULTANT.value)
        self.force_login_user(consultant.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertForbidden(response)

    def test_forbid_search_for_package_matrix_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertForbidden(response)

    def test_unauthorized_search_for_package_matrix(self):
        response = self.client.get('/api/projects/5/package-matrix/activities/', {'package': 3})

        self.assertUnauthorized(response)

    def test_search_with_handover_documents_by_staff(self):
        self._log_in_as_staff(project=5)
        url = reverse('handover_document-package_activities-list')
        response = self.client.get(url, {'has_handover_documents': True, 'project': [5]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_with_handover_documents_by_staff.json')

    def test_search_with_handover_documents_by_consultant(self):
        self._log_in_as_consultant(project=5)
        url = reverse('handover_document-package_activities-list')
        response = self.client.get(url, {'has_handover_documents': True, 'project': [5]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_with_handover_documents_by_consultant.json')

    def test_search_with_handover_documents_by_subcontractor(self):
        self._log_in_as_subcontractor(project=5)
        url = reverse('handover_document-package_activities-list')
        response = self.client.get(url, {'has_handover_documents': True, 'project': [5]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_activity/get_with_handover_documents_by_subcontractor.json')

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('package_activities_generate_csv'))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Activity CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_activity/csv_report_created.html'
            }
        ])
