from unittest import mock

import pendulum
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Exists, OuterRef
from django.urls import reverse
from django_rq import get_worker

from api.tests.test import TransactionTestCase, data_provider

from api.models import Subtask, Task, Recipient, SubtaskUpdate, QualityIssue, QualityIssueUpdate, ProjectUser, User, \
    FloorPlanAreaPin


class SubtaskTest(TransactionTestCase):
    fixtures = ['api/tests/fixtures/dumps/subtasks.json']
    fss = FileSystemStorage()
    WORK_PROJECT_ID = 5
    PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS = 6

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
    def test_create_by_project_staff(self):
        self.generate_and_save_fake_image('broom.png')

        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)

        self.assertDatabaseHas(Subtask, {'id': response.data['id'], 'files_count': 2})
        self.assertDatabaseHas(Recipient, {'email': 'tom_dvaer@gmail.com'})
        self.assertDatabaseHas(Recipient, {'email': 'tim_robinson@gmail.com', 'first_name': 'Tim', 'last_name': 'Robinson'})
        self.assertDatabaseHas(SubtaskUpdate, {'comment': 'new subtask test', 'user': 2,
                                               'new_data__status': 'in_progress', 'new_data__company': 2})

        # Check that updates from quality issue was copied.
        self.assertDatabaseHas(SubtaskUpdate, {'user': 1,
                                               'new_data': {'status': 'under_review', 'description': 'Oh! My! Goodness!'},
                                               'subtask__description': 'new subtask test'})

        # Check sync create for updates.
        self.assertDatabaseHas(QualityIssue, {'pk': 7, 'status': QualityIssue.Status.IN_PROGRESS,
                                              'description': new_subtask['description'],
                                              'attachments__id__in': new_subtask['files']})
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue': 7,
            'old_data': {
                'status': QualityIssue.Status.UNDER_REVIEW,
                'attachments': [1, 2, 3],
                'description': 'Test quality issue'
            },
            'new_data': {
                'status': QualityIssue.Status.IN_PROGRESS,
                'attachments': [1, 2],
                'description': 'new subtask test'
            },
            'user': 2
        })
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/notify_quality_issue_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/notify_quality_issue_multiplex_as_recipient.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/notify_quality_issue_recipients.html'
            }
        ])
        self.assertEventsExist('/subtask/create_events_assertion.json')

    def test_create_by_staff_without_recipients(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_without_recipients.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Notice - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/notify_multiplex_new_subtask_without_recipients.html'
            }
        ])

    def test_create_by_staff_based_on_quality_issue_without_recipients(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_based_on_quality_issue_without_recipients.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/notify_quality_issue_multiplex_without_recipients.html'
            }
        ])

    def test_create_with_company_not_from_white_list(self):
        project_staff = self._get_superuser()
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')
        new_subtask['company'] = 1

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"company":["You should select only companies that assigned on package activities."]}')

    def test_forbid_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertForbidden(response)

    def test_create_with_invalid_quality_issue_from_other_project(self):
        superuser = self._get_superuser()
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')
        new_subtask['quality_issue'] = QualityIssue.objects.filter(~Q(location_matrix__project=self.WORK_PROJECT_ID), subtask__isnull=True).first().pk

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"quality_issue":["The quality issue should be related to the same project as the subtask."]}')

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        content_type = ContentType.objects.get_for_model(Subtask)
        superuser = self._get_superuser()
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)
        self.assertDatabaseHas(FloorPlanAreaPin, {'content_type': content_type, **new_subtask['floor_plan_area_pin']})

    def test_unauthorized_create(self):
        new_subtask = self.load_request_fixture('/subtask/new_subtask.json')
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertUnauthorized(response)

    def test_create_for_quality_issue_in_invalid_status(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture(
            '/subtask/new_subtask_for_quality_issue_in_invalid_status.json'
        )

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)

    def test_create_with_client_instead_of_subcontractor(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_with_client_instead_of_subcontractor.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)

    def test_create_with_non_project_subcontractor(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_with_non_project_subcontractor.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)

    def test_create_with_quality_issue_from_different_project(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_with_quality_issue_from_different_project.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertBadRequest(response)

    def test_create_with_created_at(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_subtask_created_at.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)
        self.assertEquals(pendulum.parse(response.data['created_at']), pendulum.parse(new_subtask['created_at']))
        self.assertEventsExist('/subtask/create_with_created_at_events_assertion.json')

    def test_bulk_create_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/bulk/', new_subtask)

        self.assertNoContent(response)
        self.assertEquals(
            Subtask.objects.filter(
                description=new_subtask['description'],
                user=2,
                due_date=new_subtask['due_date']
            ).count(), 3)
        self.assertEquals(
            SubtaskUpdate.objects.filter(
                comment=new_subtask['description'],
                new_data={'status': 'in_progress', 'company': None},
                user=2
            ).count(), 3)
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_first.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_second.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_third.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_fourth.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Meeting room',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_sixth.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Meeting room',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtask/bulk_created_seventh.html'
            },
        ])
        self.assertEventsExist('/subtask/bulk_create_events_assertion.json')

    def test_forbid_bulk_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/bulk/', new_subtask)

        self.assertForbidden(response)

    def test_bulk_create_by_superuser(self):
        superuser = self._get_superuser()
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/bulk/', new_subtask)

        self.assertNoContent(response)

    def test_unauthorized_bulk_create(self):
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks.json')
        response = self.client.post('/api/projects/5/subtasks/bulk/', new_subtask)

        self.assertUnauthorized(response)

    def test_bulk_create_from_quality_issues_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks_from_quality_issues.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/quality-issues/subtasks/bulk/', new_subtask)

        self.assertNoContent(response)

        quality_issue = QualityIssue.objects.filter(pk=7).prefetch_related('attachments').get()
        attachments = quality_issue.attachments.all().values_list('id', flat=True)

        self.assertDatabaseHas(Subtask, {'quality_issue': quality_issue, 'due_date': '2020-01-04 00:00:00',
                                         'status': Subtask.Status.IN_PROGRESS, 'description': quality_issue.description,
                                         'response_due_date': quality_issue.due_date, 'company': 3, 'task': 2,
                                         'files__id__in': attachments})

        quality_issue = QualityIssue.objects.filter(pk=3).prefetch_related('attachments').get()
        attachments = quality_issue.attachments.all().values_list('id', flat=True)

        self.assertDatabaseHas(Subtask, {'quality_issue': quality_issue, 'due_date': '2020-01-04 00:00:00',
                                         'status': Subtask.Status.IN_PROGRESS, 'description': quality_issue.description,
                                         'response_due_date': quality_issue.due_date, 'company': 3, 'task': 2,
                                         'files__id__in': attachments})

    def test_bulk_create_from_quality_issues_with_location_matrix_without_task(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/quality-issues/subtasks/bulk/', {
            'quality_issues': [1, 8, 9],
            'company': 3,
            'task': 2,
        })

        self.assertBadRequest(response)
        self.assertEqualsFixture(response.data, '/subtask/error_message_for_invalid_location_matrix_without_task.json')

    def test_forbid_bulk_create_from_quality_issues_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks_from_quality_issues.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/quality-issues/subtasks/bulk/', new_subtask)

        self.assertForbidden(response)

    def test_bulk_create_from_quality_issues_by_superuser(self):
        superuser = self._get_superuser()
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks_from_quality_issues.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/subtasks/bulk/', new_subtask)

        self.assertNoContent(response)

    def test_unauthorized_bulk_create_from_quality_issues(self):
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks_from_quality_issues.json')
        response = self.client.post('/api/projects/5/quality-issues/subtasks/bulk/', new_subtask)

        self.assertUnauthorized(response)

    def test_forbid_create_with_subcontractor_by_non_staff(self):
        new_subtask = self.load_request_fixture('/subtask/new_bulk_subtasks.json')

        self.force_login_user(6)
        response = self.client.post('/api/projects/5/subtasks/bulk/', new_subtask)

        self.assertForbidden(response)

    def get_filters_for_test_search_creators(self):
        return (
            (
                {'search': 'Bradwood'},
                '/subtask/search_creators_by_first_name.json'
            ),
            (
                {'search': 'Feat'},
                '/subtask/search_creators_by_last_name.json'
            ),
            (
                {'search': 'cool.brad+1'},
                '/subtask/search_creators_by_email.json'
            ),
        )

    @data_provider(get_filters_for_test_search_creators)
    def test_search_creators_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_test_search_creators)
    def test_search_creators_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_creators_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search_creators(self):
        response = self.client.get('/api/projects/5/subtasks/creators/', {'all': 1})

        self.assertUnauthorized(response)

    def test_get_creators_by_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_creators.json')

    def test_forbid_get_creators_by_subcontractor_from_differ_company_as_project_user(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/')

        self.assertForbidden(response)

    def test_get_companies_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/companies/', {'sort': 'id,status'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_companies.json')

    def test_forbid_get_subcontractors_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/companies/')

        self.assertForbidden(response)

    def test_get_companies_by_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/companies/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_companies.json')

    def test_forbid_get_subcontractors_by_subcontractor_from_company_differ_than_project_user(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/companies/')

        self.assertForbidden(response)

    def test_unauthorized_get_subcontractors(self):
        response = self.client.get('/api/projects/5/subtasks/companies/')

        self.assertUnauthorized(response)

    def test_forbid_get_creators_by_subcontractor_from_company_differ_than_project_user(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/creators/')

        self.assertForbidden(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask.json')

    def test_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertForbidden(response)

    def test_get_by_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask.json')

    def test_get_by_subcontractor_from_company_differ_than_project_user(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertForbidden(response)

    def test_unauthorized_get(self):
        response = self.client.get('/api/projects/5/subtasks/1/')

        self.assertUnauthorized(response)

    def test_get_with_expand_fields(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/', {'expand': [
            'expanded_task.expanded_package',
            'expanded_closed_files',
            'expanded_quality_issue',
            'expanded_user',
            'expanded_company',
            'expanded_files',
            'expanded_updates',
            'expanded_last_confirmed_update.expanded_previous_status',
            'expanded_last_recipients',
            'expanded_last_update',
            'expanded_status_date'
        ]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_with_expand_fields.json')

    def test_get_count_by_project_user(self):
        project_user = self._get_user(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_user.pk)
        response = self.client.get('/api/projects/5/subtasks/count/', {'area': 'Meeting room'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_count_by_staff.json')

    def test_get_count_by_non_project_user(self):
        non_project_user = self._get_user(~Q(project=self.WORK_PROJECT_ID), is_superuser=False, is_staff=False)
        self.force_login_user(non_project_user.pk)
        response = self.client.get('/api/projects/5/subtasks/count/')

        self.assertForbidden(response)

    def test_unauthorized_get_count(self):
        response = self.client.get('/api/projects/5/subtasks/count/')

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/subtasks/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Subtask, 2)
        self.assertEventsExist('/subtask/delete_events_assertions.json')

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/subtasks/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Subtask, 2)

    def test_forbid_delete_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.delete('/api/projects/5/subtasks/2/')

        self.assertForbidden(response)

    def test_delete_with_changing_status_of_related_task(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/projects/5/subtasks/7/')

        self.assertNoContent(response)
        self.assertDatabaseHas(Task, {'pk': 5, 'status': Task.Statuses.NOT_APPLICABLE})
        self.assertEventsExist('/subtask/delete_with_changing_task_status_events_assertion.json')

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/subtasks/2/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'status'},
                '/subtask/get_all_sorted_by_status.json'
            ),
            (
                {'all': True, 'sort': 'user'},
                '/subtask/get_all_sorted_by_user.json'
            ),
            (
                {'all': True, 'sort': 'files_count'},
                '/subtask/get_all_sorted_by_files_count.json'
            ),
            (
                {'all': True, 'sort': 'updated_at'},
                '/subtask/get_all_sorted_by_asc_updated_at.json'
            ),
            (
                {'all': True, 'sort': '-updated_at'},
                '/subtask/get_all_sorted_by_desc_updated_at.json'
            ),
            (
                {'sort': 'default_sort'},
                '/subtask/get_with_default_sort.json'
            ),
            (
                {'all': True, 'sort': 'subcontractor'},
                '/subtask/get_all_sorted_by_subcontractor.json'
            ), (
                {'all': True, 'sort': 'due_date'},
                '/subtask/get_all_sorted_by_due_date.json'
            ),
            (
                {'sort': 'status_date'},
                '/subtask/get_ordered_by_status_date.json'
            ),
            (
                {'all': True},
                '/subtask/get_all.json'
            ),
            (
                {'all': True, 'expand': 'expanded_task.expanded_package'},
                '/subtask/get_all_with_expand_field.json'
            ),
            (
                {'all': True, 'expand': 'expanded_last_status_change_update'},
                '/subtask/get_all_with_expand_last_status_change_update.json'
            ),
            (
                {'building': ['Building A']},
                '/subtask/get_by_building.json'
            ),
            (
                {'area': ['Hall', 'Meeting room']},
                '/subtask/get_by_area.json'
            ),
            (
                {'level': 'A'},
                '/subtask/get_by_level.json'
            ),
            (
                {'package': 4},
                '/subtask/get_by_package.json'
            ),
            (
                {'package_activity': 2},
                '/subtask/get_by_package_activity.json'
            ),
            (
                {'package_activity_task': [2]},
                '/subtask/get_by_package_activity_task.json'
            ),
            (
                {'user': [2]},
                '/subtask/get_by_user.json'
            ),
            (
                {'search': 'build'},
                '/subtask/search_by_building.json'
            ),
            (
                {'search': 'A'},
                '/subtask/search_by_level.json'
            ),
            (
                {'search': 'room'},
                '/subtask/search_by_area.json'
            ),
            (
                {'search': 'secon'},
                '/subtask/search_by_activity_name.json'
            ),
            (
                {'search': 'gan_gsta@gmail.com'},
                '/subtask/search_by_recipient_email.json'
            ),
            (
                {'search': 'soyer'},
                '/subtask/search_by_recipient_last_name.json'
            ),
            (
                {'search': 'joshua'},
                '/subtask/search_by_recipient_first_name.json'
            ),
            (
                {'search': 'desc'},
                '/subtask/search_by_activity_task_description.json'
            ),
            (
                {'page': 2, 'per_page': 1},
                '/subtask/get_all_page_per_page.json'
            ),
            (
                {'all_with_activity': True, 'all': True},
                '/subtask/get_all_with_activity.json'
            ),
            (
                {'is_defect': True},
                '/subtask/filter_by_is_defect.json'
            ),
            (
                {'except_status': [Subtask.Status.IN_PROGRESS]},
                '/subtask/filter_by_status_except.json'
            ),
            (
                {'company': [2]},
                '/subtask/get_by_subcontractor.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-07-29T00:00:00', 'created_at__lte': '2020-07-29T23:59:59'},
                '/subtask/filter_by_created_at_range.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-07-29T12:27:00', 'updated_at__lte': '2020-07-29T12:29:00'},
                '/subtask/filter_by_updated_at_range.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/subtasks/', {'all': 1})

        self.assertUnauthorized(response)

    @data_provider(get_filters)
    def test_search_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_as_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/', {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_all_by_subcontractor.json')

    def test_forbid_list_as_subcontractor_from_differ_company_than_project_user(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/', {'all': True})

        self.assertForbidden(response)

    def test_add_files_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/add/', {'files': [3, 4]})

        self.assertOk(response)
        self.assertDatabaseHas(Subtask, {'files__pk': 3, 'pk': 1})
        self.assertDatabaseHas(Subtask, {'files__pk': 4, 'pk': 1})
        self.assertEventsExist('/subtask/add_files_events_assertion.json')

    def test_add_files_by_non_project_staff(self):
        project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/add/', {'files': [3, 4]})

        self.assertForbidden(response)

    def test_add_files_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/add/', {'files': [3, 4]})

        self.assertOk(response)

    def test_remove_files_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/remove/', {'files': [1, 2]})

        self.assertOk(response)
        self.assertDatabaseMissing(Subtask, {'files__pk': 1, 'pk': 1})
        self.assertDatabaseMissing(Subtask, {'files__pk': 2, 'pk': 1})
        self.assertEventsExist('/subtask/remove_files_events_assertion.json')

    def test_forbid_remove_files_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/remove/', {'files': [1, 2]})

        self.assertForbidden(response)

    def test_remove_files_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/files/remove/', {'files': [1, 2]})

        self.assertOk(response)

    def test_unauthorized_remove(self):
        response = self.client.post('/api/projects/5/subtasks/1/files/remove/', {'files': [1, 2]})

        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/csv/', {'sort': 'files_count', 'area': 'Hall'})

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Rework and Defects CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/subtask/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    def test_get_csv_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/csv/', {'sort': 'files_count', 'area': 'Hall'})

        self.assertOk(response)

    def test_forbid_get_csv_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/csv/', {'sort': 'files_count', 'area': 'Hall'})

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    def test_get_csv_by_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/csv/', {'sort': 'files_count', 'area': 'Hall'})

        self.assertOk(response)

    def test_unauthorized_get_csv(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))
        response = self.client.get('/api/projects/5/subtasks/csv/', {'sort': 'files_count', 'area': 'Hall'})

        self.assertUnauthorized(response)

    @mock.patch('api.utilities.report_generators.SubtaskReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/pdf/')

        self.assertOk(response)
        self.assertEmailEquals([
            {
                'subject': 'Rework and Defects PDF report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/subtask/pdf_report_created.html'
            }
        ])

    @mock.patch('api.utilities.report_generators.SubtaskReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORK_PROJECT_ID)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/pdf/')

        self.assertOk(response)

    def test_forbid_get_pdf_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORK_PROJECT_ID))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/pdf/')

        self.assertForbidden(response)

    @mock.patch('api.utilities.report_generators.SubtaskReportGenerator.generatePdf', mock_function_with_arguments)
    @mock.patch('api.services.media_entity_service.MediaEntityService.save_report', mock_save_report)
    def test_get_pdf_by_subcontractor_from_same_company_as_project_user(self):
        subcontractor = self._get_user(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'), project=self.WORK_PROJECT_ID)),
                                       groups=User.Group.SUBCONTRACTOR.value)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/pdf/')

        self.assertOk(response)

    def test_unauthorized_get_pdf(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))
        response = self.client.get('/api/projects/5/subtasks/pdf/')

        self.assertUnauthorized(response)

    def test_create_with_quality_issue_location_change(self):
        new_subtask = self.load_request_fixture('/subtask/new_subtask_with_quality_issue_location_change.json')

        self.force_login_user(2)
        response = self.client.post('/api/projects/5/subtasks/', new_subtask)

        self.assertCreated(response)
        self.assertDatabaseHas(Recipient, {'email': 'tom_dvaer@gmail.com'})
        self.assertDatabaseHas(Recipient, {'email': 'tim_robinson@gmail.com',
                                           'first_name': 'Tim',
                                           'last_name': 'Robinson'})
        self.assertDatabaseHas(SubtaskUpdate, {'comment': 'new subtask test',
                                               'new_data': {'status': 'in_progress', 'company': 3},
                                               'user': 2})
        self.assertDatabaseHas(QualityIssueUpdate, {'old_data': {'status': 'under_review', 'attachments': [1, 2, 3], 'description': 'Test quality issue', 'location_matrix': 1},
                                                    'new_data': {'status': 'in_progress', 'attachments': [1, 2], 'description': 'new subtask test', 'location_matrix': 2},
                                                    'user': 2})
        self.assertDatabaseMissing(QualityIssue, {'pk': 7, 'location_matrix': 1})
        self.assertDatabaseHas(QualityIssue, {'pk': 7, 'location_matrix': 2})

    def test_search_via_api_key(self):
        response = self.client.get('/api/projects/5/subtasks/', [],
                                   HTTP_AUTHORIZATION='Api-Key gMopOTBs.pbVLHfuVcK6gvx5yrSS302S4Faw6hY6w')

        self.assertOk(response)

    def test_get_subtasks_by_client(self):
        project_client = self._get_client(project=self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS)
        self.force_login_user(project_client.id)
        response = self.client.get(reverse('subtasks_list', kwargs={'project_pk': self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS}), {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_all_by_client.json')

    def test_forbid_get_subtask_by_non_project_client(self):
        user_client = self._get_client(~Q(project=self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS))
        self.force_login_user(user_client.id)
        response = self.client.get(reverse('subtasks_list', kwargs={'project_pk': self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS}))
        
        self.assertForbidden(response)

    def test_forbid_get_subtask_by_project_client(self):
        user_client = self._get_client(project=self.WORK_PROJECT_ID)
        self.force_login_user(user_client.id)
        response = self.client.get(reverse('subtasks_list', kwargs={'project_pk': self.WORK_PROJECT_ID}))

        self.assertForbidden(response)

    def test_remove_subtasks_on_location_matrix_delete(self):
        sync_data = [{'id': 1, 'delete_matrix': True}]
        url = reverse('location_matrix_bulk_create', kwargs={'project_pk': 5})
        subtasks = Subtask.objects.filter(
            ~Q(status__in=[Subtask.Status.REMOVED, Subtask.Status.CLOSED]),
            task__location_matrix=1
        ).all()

        self._log_in_as_staff(project=5, editmode__project=5)
        response = self.client.post(url, sync_data)

        self.assertOk(response)
        for subtask in subtasks:
            self.assertDatabaseHas(Subtask, {'id': subtask.id, 'status': Subtask.Status.REMOVED})

    def test_get_files_by_superuser(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_files.json')

    def test_get_files_by_project_staff(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        self._log_in_as_staff(project=self.WORK_PROJECT_ID)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_files.json')

    def test_get_files_by_non_project_staff(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        self._log_in_as_staff(~Q(project=self.WORK_PROJECT_ID))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_files_by_subcontractor_from_same_company_as_project_user(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        self._log_in_as_subcontractor(Exists(ProjectUser.objects.filter(user__company=OuterRef('company'),
                                                                        project=self.WORK_PROJECT_ID)))
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_files.json')

    def test_get_files_by_subcontractor_from_company_differ_than_project_user(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        self._log_in_as_subcontractor(~Exists(ProjectUser.objects.filter(user__company=OuterRef('company'),
                                                                         project=self.WORK_PROJECT_ID)))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_unauthorized_get_files(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1,
        })
        response = self.client.get(url)

        self.assertUnauthorized(response)

    def test_get_subtasks_files_by_client(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS,
            'pk': 12
        })
        self._log_in_as_client(project=self.PROJECT_WITH_VISIBLE_FOR_CLIENTS_SUBTASKS)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtask/get_subtask_files_by_client.json')

    def test_forbid_get_subtasks_files_by_client(self):
        url = reverse('subtasks_files', kwargs={
            'project_pk': self.WORK_PROJECT_ID,
            'pk': 1
        })
        self._log_in_as_client(project=self.WORK_PROJECT_ID)
        response = self.client.get(url)

        self.assertForbidden(response)
