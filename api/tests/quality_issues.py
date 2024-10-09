from unittest import mock

import pendulum
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import QualityIssue, QualityIssueUpdate, User, FloorPlanAreaPin
from api.tests.test import TestCase, data_provider


class QualityIssueTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/quality_issue.json']
    fss = FileSystemStorage()

    WORKING_PROJECT = 5

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

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        content_type = ContentType.objects.get_for_model(QualityIssue)
        superuser = self._get_superuser()
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        del new_quality_issue['attachments']
        del new_quality_issue['recipients']

        floor_plan_area_pin = new_quality_issue.pop('floor_plan_area_pin')

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'status': QualityIssue.Status.UNDER_REVIEW, **new_quality_issue})
        self.assertDatabaseHas(QualityIssueUpdate, {'comment': 'Baby shark dodo-dodo-dodo!',
                                                    'new_data__status': QualityIssue.Status.UNDER_REVIEW,
                                                    'user': 1})

        # Make sure that old quality issue was transited to the status Removed
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.REMOVED})
        self.assertDatabaseHas(QualityIssueUpdate, {'quality_issue': 1,
                                                    'new_data': {'status': QualityIssue.Status.REMOVED},
                                                    'old_data': {'status': QualityIssue.Status.UNDER_REVIEW},
                                                    'user': 1})

        self.assertDatabaseHas(QualityIssueUpdate, {'comment': 'Quality Issue was created based on Q-1 (R-5).',
                                                    'new_data': {'status': QualityIssue.Status.UNDER_REVIEW},
                                                    'old_data': {'status': QualityIssue.Status.UNDER_REVIEW},
                                                    'user': 1})

        self.assertDatabaseHas(FloorPlanAreaPin, {'content_type': content_type, **floor_plan_area_pin})

        self.assertEmailEquals([
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_notify_multiplex.html'
            },
            {
                'to': ['stan.smith@long.com', 'mimo.stule@bokom.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_notify_recipients.html'
            },
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_created_to_multiplex.html'
            },
            {
                'to': ['stan.smith@long.com', 'mimo.stule@bokom.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_created_to_recipients.html'
            }
        ])

        self.assertEventsExist('/quality_issues/create_events_assertion.json')

    def test_create_by_superuser_without_recipients(self):
        superuser = self._get_superuser()
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue_without_recipients.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertCreated(response)

        self.assertEmailEquals([
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_created_without_recipients_subtask_status_change.html'
            },
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Quality Issue Notice – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/quality_issue_created_without_recipients.html'
            }
        ])

    def test_create_by_superuser_with_invalid_response_due_date(self):
        superuser = self._get_superuser()
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue_with_invalid_response_category.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"response_category":["You should select response category from same project as quality issue."]}')

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_by_project_client(self):
        self.generate_and_save_fake_image('broom.png')

        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertCreated(response)

    def test_forbid_create_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(non_project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertForbidden(response)

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_by_project_consultant(self):
        self.generate_and_save_fake_image('broom.png')

        project_client = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertCreated(response)

    def test_forbid_create_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(non_project_consultant.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertForbidden(response)

    def test_create_with_invalid_location_matrix_by_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        new_quality_issue = self.load_request_fixture(
            '/quality_issue/create_quality_issue_with_invalid_location_matrix.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertBadRequest(response)

    def test_create_with_invalid_location_matrix_by_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        new_quality_issue = self.load_request_fixture(
            '/quality_issue/create_quality_issue_with_invalid_location_matrix.json')

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertBadRequest(response)

    def test_forbid_create_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_quality_issue = self.load_request_fixture('/quality_issue/create_quality_issue.json')

        response = self.client.post('/api/projects/5/quality-issues/', new_quality_issue)

        self.assertUnauthorized(response)

    def test_get_count_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/count/', {'area': 'Meeting room'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue_count_by_staff.json')

    def test_get_count_by_project_user(self):
        project_user = self._get_user(project=5)
        self.force_login_user(project_user.pk)
        response = self.client.get('/api/projects/5/quality-issues/count/', {'area': 'Meeting room'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue_count_by_staff.json')

    def test_get_count_by_non_project_user(self):
        non_project_user = self._get_user(~Q(project=5))
        self.force_login_user(non_project_user.pk)
        response = self.client.get('/api/projects/5/quality-issues/count/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue_count_by_subcontractor.json')

    def test_unauthorized_get_count(self):
        response = self.client.get('/api/projects/5/quality-issues/count/')

        self.assertUnauthorized(response)

    def test_update_by_superuser(self):
        superuser = self._get_superuser()
        update_quality_issue = self.load_request_fixture('/quality_issue/update_quality_issue.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/quality-issues/1/', update_quality_issue)

        self.assertOk(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, **update_quality_issue})

    def test_update_by_project_user(self):
        project_user = self._get_user(project=5)
        update_quality_issue = self.load_request_fixture('/quality_issue/update_quality_issue.json')

        self.force_login_user(project_user.pk)
        response = self.client.put('/api/projects/5/quality-issues/1/', update_quality_issue)

        self.assertOk(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, **update_quality_issue})

    def test_forbid_update_by_non_project_user(self):
        non_project_user = self._get_user(~Q(project=5), is_staff=False, is_superuser=False)
        update_quality_issue = self.load_request_fixture('/quality_issue/update_quality_issue.json')

        self.force_login_user(non_project_user.pk)
        response = self.client.put('/api/projects/5/quality-issues/1/', update_quality_issue)

        self.assertForbidden(response)

    def test_update_due_date_for_invalid_state(self):
        superuser = self._get_superuser()
        update_quality_issue = self.load_request_fixture('/quality_issue/update_quality_issue.json')
        update_quality_issue['due_date'] = '2021-01-01'

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/projects/5/quality-issues/2/', update_quality_issue)

        self.assertBadRequest(response)

    def test_unauthorized_update(self):
        update_quality_issue = self.load_request_fixture('/quality_issue/update_quality_issue.json')
        response = self.client.put('/api/projects/5/quality-issues/1/', update_quality_issue)

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/quality-issues/3/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(QualityIssue, 3)
        self.assertEventsExist('/quality_issues/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/projects/5/quality-issues/3/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/quality-issues/3/')

        self.assertUnauthorized(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/3/',
                                   {'expand': ['expanded_location_matrix', 'expanded_last_recipients.expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update', 'expanded_subtasks',
                                               'expanded_last_update.expanded_user', 'expanded_user']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/3/',
                                   {'expand': ['expanded_location_matrix', 'expanded_last_update.expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update', 'expanded_user',
                                               'expanded_last_recipients.expanded_user', 'expanded_subtasks']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue.json')

    def test_forbid_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/3/',
                                   {'expand': ['expanded_location_matrix', 'expanded_subtasks', 'expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update.status', 'expanded_last_recipients.expanded_user',
                                               'expanded_last_update.expanded_user']})

        self.assertForbidden(response)

    def test_get_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/6/',
                                   {'expand': ['expanded_location_matrix', 'expanded_subtasks', 'expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update', 'expanded_last_recipients.expanded_user',
                                               'expanded_last_update.expanded_user']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue_by_client.json')

    def test_forbid_get_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/3/',
                                   {'expand': ['expanded_location_matrix', 'expanded_subtasks', 'expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update.status', 'expanded_last_recipients.expanded_user',
                                               'expanded_last_update.expanded_user']})

        self.assertForbidden(response)

    def test_get_by_project_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/7/',
                                   {'expand': ['expanded_location_matrix', 'expanded_subtasks', 'expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update', 'expanded_last_recipients.expanded_user',
                                               'expanded_last_update.expanded_user']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/get_quality_issue_by_consultant.json')

    def test_forbid_get_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/3/',
                                   {'expand': ['expanded_location_matrix', 'expanded_subtasks', 'expanded_user',
                                               'expanded_attachments', 'expanded_in_work_subtasks_count',
                                               'expanded_last_confirmed_update.status', 'expanded_last_recipients.expanded_user',
                                               'expanded_last_update.expanded_user']})

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/quality-issues/3/')

        self.assertUnauthorized(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True})

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': '-created_at', 'expand': ['expanded_last_confirmed_update.expanded_previous_status']},
                '/quality_issues/get_all_desc_order.json'
            ),
            (
                {'all': True, 'expand': ['expanded_last_status_change_update']},
                '/quality_issues/get_all_with_expand_last_status_change_update.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/quality_issues/get_page_per_page.json'
            ),
            (
                {'status': "under_review"},
                '/quality_issues/get_under_review.json'
            ),
            (
                {
                    "building": "Building A",
                    "level": "A",
                    "area": "Meeting room"
                },
                '/quality_issues/get_by_locations.json'
            ),
            (
                {'package': 4},
                '/quality_issues/get_by_package.json'
            ),
            (
                {'package_activity': 2},
                '/quality_issues/get_by_package_activity.json'
            ),
            (
                {'except_status': [QualityIssue.Status.UNDER_REVIEW]},
                '/quality_issues/filter_by_status_except.json'
            ),
            (
                {'sort': 'default_sort'},
                '/quality_issues/get_sorted_by_default.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-09-23T00:00:00', 'created_at__lte': '2020-09-24T00:00:00'},
                '/quality_issues/filter_by_created_at_range.json'
            ),
            (
                {
                    'subtask_is_defect': True,
                    'expand': ['expanded_subtasks']
                },
                '/quality_issues/filter_by_subtask_is_defect.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-09-24T00:00:00', 'updated_at__lte': '2020-09-25T00:00:00'},
                '/quality_issues/filter_by_updated_at_range.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': 1})

        self.assertForbidden(response)

    def test_search_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True, 'sort': '-created_at'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/search_as_client.json')

    def test_forbid_search_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True, 'sort': '-created_at'})

        self.assertForbidden(response)

    def test_search_by_project_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True, 'sort': '-created_at'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/search_as_consultant.json')

    def test_forbid_search_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True, 'sort': '-created_at'})

        self.assertForbidden(response)

    def test_forbid_search_by_subcontractor(self):
        project_subcontractor = self._get_user(project=5, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/quality-issues/', {'all': True, 'sort': '-created_at'})

        self.assertForbidden(response)

    def get_filters_for_test_search_creators(self):
        return (
            (
                {'search': 'Bradwood'},
                '/quality_issues/search_creators_by_first_name.json'
            ),
            (
                {'search': 'Feat'},
                '/quality_issues/search_creators_by_last_name.json'
            ),
            (
                {'search': 'cool.brad+1'},
                '/quality_issues/search_creators_by_email.json'
            ),
        )

    @data_provider(get_filters_for_test_search_creators)
    def test_search_creators_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_test_search_creators)
    def test_search_creators_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_creators_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertForbidden(response)

    def test_search_creators_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/search_by_project_client.json')

    def test_search_creators_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertForbidden(response)

    def test_search_creators_by_project_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/search_by_project_consultant.json')

    def test_forbid_search_creators_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search_creators(self):
        response = self.client.get('/api/projects/5/quality-issues/creators/', {'all': 1})

        self.assertUnauthorized(response)

    @mock.patch('api.utilities.report_generators.QualityIssueReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Quality Issue PDF report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/quality_issues/pdf_report_created.html'
            }
        ])

    @mock.patch('api.utilities.report_generators.QualityIssueReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertOk(response)

    @mock.patch('api.utilities.report_generators.QualityIssueReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertOk(response)

    def test_forbid_get_pdf_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertForbidden(response)

    @mock.patch('api.utilities.report_generators.QualityIssueReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_project_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertOk(response)

    def test_forbid_get_pdf_by_non_project_consultant(self):
        project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertForbidden(response)

    def test_forbid_get_pdf_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))

        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertForbidden(response)

    def test_unauthorized_get_pdf(self):
        response = self.client.get('/api/projects/5/quality-issues/pdf/')

        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Quality Issue CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/quality_issues/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_client(self):
        project_client = self._get_user(project=5, groups=User.Group.CLIENT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertOk(response)

    def test_forbid_get_csv_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=5), groups=User.Group.CLIENT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_consultant(self):
        project_consultant = self._get_user(project=5, groups=User.Group.CONSULTANT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertOk(response)

    def test_forbid_get_csv_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=5), groups=User.Group.CONSULTANT.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    def test_get_csv_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/', {'sort': 'building'})

        self.assertOk(response)

    def test_forbid_get_csv_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))

        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/csv/')

        self.assertForbidden(response)

    def test_unauthorized_get_csv(self):
        response = self.client.get('/api/projects/5/quality-issues/csv/')

        self.assertUnauthorized(response)

    def test_bulk_create_by_superuser(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.post(url, request_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/bulk_create_by_superuser.json')

        del request_data['recipients']

        building = request_data.pop('building')
        level = request_data.pop('level')
        areas = request_data.pop('area')
        attachments = request_data.pop('attachments')

        self.assertEquals(
            2,
            QualityIssue.objects.filter(**{
                **request_data,
                'location_matrix__building': building,
                'location_matrix__level': level,
                'location_matrix__area__in': areas,
                'attachments__id__in': attachments,
            }).count()
        )

    def test_bulk_create_by_project_client(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/bulk_create_by_project_client.json')

        del request_data['recipients']

        building = request_data.pop('building')
        level = request_data.pop('level')
        areas = request_data.pop('area')
        attachments = request_data.pop('attachments')

        self.assertEquals(
            2,
            QualityIssue.objects.filter(**{
                **request_data,
                'location_matrix__building': building,
                'location_matrix__level': level,
                'location_matrix__area__in': areas,
                'attachments__id__in': attachments,
            }).count()
        )

    def test_bulk_create_by_project_consultant(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issues/bulk_create_by_project_consultant.json')

        del request_data['recipients']

        building = request_data.pop('building')
        level = request_data.pop('level')
        areas = request_data.pop('area')
        attachments = request_data.pop('attachments')

        self.assertEquals(
            2,
            QualityIssue.objects.filter(**{
                **request_data,
                'location_matrix__building': building,
                'location_matrix__level': level,
                'location_matrix__area__in': areas,
                'attachments__id__in': attachments,
            }).count()
        )

    def test_bulk_create_by_non_project_client(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_non_project_consultant(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_project_admin(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_non_project_admin(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_project_manager(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_non_project_manager(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_bulk_create_by_non_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue/bulk_create_quality_issue.json')
        url = reverse('quality_issue-bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)
