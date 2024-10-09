from django.db.models import Q
from freezegun import freeze_time
from rest_framework.reverse import reverse

from api.models import Recipient, QualityIssueUpdate, QualityIssue, Subtask, SubtaskUpdate, User
from api.tests.test import TestCase, data_provider


class QualityIssueUpdateTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/quality_issue_update.json']
    WORKING_PROJECT = 5

    def test_create_by_consultant(self):
        consultant = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CONSULTANT.value)
        new_quality_issue_update = self.load_request_fixture('/quality_issue_updates/new_quality_issue_update.json')

        self.force_login_user(consultant.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        del new_quality_issue_update['files']
        recipients = new_quality_issue_update.pop('recipients')

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssueUpdate, new_quality_issue_update)
        self.assertDatabaseHas(
            QualityIssue, {'pk': 1, 'status': new_quality_issue_update['new_data']['status'], 'user__pk': 1}
        )

        for recipient in recipients:
            self.assertDatabaseHas(Recipient, recipient)

        self.assertEmailEquals([
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/create_by_client_multiplex.html'
            },
            {
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issues/create_by_client_recipients.html'
            }
        ])

        self.assertEventsExist('/quality_issue_update/create_events_assertion.json')

    def test_change_status_for_closed_quality_issue(self):
        superuser = self._get_superuser()
        new_quality_issue_update = self.load_request_fixture('/quality_issue_updates/new_quality_issue_update.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/3/updates/', new_quality_issue_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status for closed quality issue."]}')

    def test_create_by_consultant_for_contested_quality_issue(self):
        consultant = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CONSULTANT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/new_quality_issue_update_for_contested_by_consultant.json')

        self.force_login_user(consultant.pk)
        response = self.client.post('/api/projects/5/quality-issues/6/updates/', new_quality_issue_update)

        del new_quality_issue_update['files']
        recipients = new_quality_issue_update.pop('recipients')

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssueUpdate, new_quality_issue_update)
        self.assertDatabaseHas(QualityIssue, {'pk': 6, 'status': new_quality_issue_update['new_data']['status'],
                                              'description': new_quality_issue_update['new_data']['description']})

        for recipient in recipients:
            self.assertDatabaseHas(Recipient, recipient)

    def test_update_rejection_reason_for_contested_quality_issue_update_by_manager(self):
        project_manager = self._get_user(project=self.WORKING_PROJECT, group=User.Group.MANAGER.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/update_rejection_reason_for_contested_quality_issue_update.json')

        self.force_login_user(project_manager.pk)
        response = self.client.post('/api/projects/5/quality-issues/6/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {
            'pk': 6,
            'status': new_quality_issue_update['new_data']['status'],
            'last_confirmed_update__comment': new_quality_issue_update['comment'],
            'last_confirmed_update__new_data__status': new_quality_issue_update['new_data']['status'],
        })

    def test_create_with_invalid_data_by_client_for_quality_issue_in_inapplicable_status(self):
        project_client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/new_quality_issue_update_for_quality_issue_in_inapplicable_status.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/2/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_create_with_invalid_data_by_consultant_for_quality_issue_in_inapplicable_status(self):
        project_consultant = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CONSULTANT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/new_quality_issue_update_for_quality_issue_in_inapplicable_status.json')

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/quality-issues/2/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_unauthorized_create(self):
        new_quality_issue_update = self.load_request_fixture('/quality_issue_updates/new_quality_issue_update.json')
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertUnauthorized(response)

    def test_forbid_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORKING_PROJECT))
        self.force_login_user(non_project_staff.pk)

        new_quality_issue_update = self.load_request_fixture('/quality_issue_updates/new_quality_issue_update.json')
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertForbidden(response)

    def test_create_incorrect_new_data(self):
        superuser = self._get_superuser()
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/new_quality_issue_update_incorrect_new_data.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_create_incorrect_new_data_incorrect_field(self):
        superuser = self._get_superuser()
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/new_quality_issue_update_incorrect_new_data_incorrect_field.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/get_quality_issue_update.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=self.WORKING_PROJECT)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/get_quality_issue_update.json')

    def test_forbid_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORKING_PROJECT))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertForbidden(response)

    def test_get_by_project_client(self):
        project_client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/get_quality_issue_update.json')

    def test_forbid_get_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=self.WORKING_PROJECT), group=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertForbidden(response)

    def test_get_by_project_consultant(self):
        project_consultant = self._get_staff(project=self.WORKING_PROJECT)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/get_quality_issue_update.json')

    def test_forbid_get_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=self.WORKING_PROJECT), group=User.Group.CLIENT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/')

        self.assertForbidden(response)

    def test_get_with_expandable_fields(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/5/updates/1/', {
            'expand': ['expanded_quality_issue', 'expanded_user', 'expanded_files', 'expanded_last_confirmed_update.expanded_previous_status']
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/get_quality_issue_update_with_expandable_fields.json')

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/quality-issues/5/updates/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(QualityIssueUpdate, 1)
        self.assertEventsExist('/quality_issue_update/delete_events_assertion.json')

    def test_forbid_delete_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/projects/5/quality-issues/5/updates/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/quality-issues/5/updates/1/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'created_at'},
                '/quality_issue_update/get_all_sorted_by_created_at.json'
            ),
            (
                {'all': True, 'sort': '-created_at'},
                '/quality_issue_update/get_all_sorted_by_created_at_desc.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=self.WORKING_PROJECT)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=self.WORKING_PROJECT))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', {'all': 1})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_client(self, filters, fixture):
        project_client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_client(self):
        non_project_client = self._get_user(~Q(project=self.WORKING_PROJECT), group=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', {'all': 1})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_project_consultant(self, filters, fixture):
        project_consultant = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Q(project=self.WORKING_PROJECT), group=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/quality-issues/4/updates/', {'all': 1})

        self.assertForbidden(response)

    def test_invalid_status_transition_by_client(self):
        project_client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_progress_to_requesting_approval.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_status_transition_with_equals_statuses(self):
        project_client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/quality_issue_update_status_transition_with_equal_statuses.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'description': new_quality_issue_update['new_data']['description']})

    def test_transform_quality_issue_status_from_in_progress_to_requesting_approval_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_progress_to_requesting_approval.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.REQUESTING_APPROVAL,
                                              'description': new_quality_issue_update['new_data']['description']})

    def test_transform_quality_issue_status_from_contested_to_declined_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_declined.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.DECLINED})

    def test_transform_quality_issue_and_related_subtasks_to_requesting_approval(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_progress_to_requesting_approval.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/2/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 2, 'status': QualityIssue.Status.REQUESTING_APPROVAL,
                                              'description': new_quality_issue_update['new_data']['description']})

        # Check that related to the quality issue subtasks' statuses changed to the "Requesting Approval"
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.REQUESTING_APPROVAL})
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.REQUESTING_APPROVAL})

    def test_transform_quality_issue_and_related_last_subtask_to_requesting_approval(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_progress_to_requesting_approval.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/9/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 9, 'status': QualityIssue.Status.REQUESTING_APPROVAL,
                                              'description': new_quality_issue_update['new_data']['description']})
        # Check that related to the quality issue subtask status changed to the "Requesting Approval"
        self.assertDatabaseHas(Subtask, {'pk': 15, 'status': Subtask.Status.REQUESTING_APPROVAL})

    def test_transform_quality_issue_status_from_in_progress_to_requesting_approval_by_client(self):
        client = self._get_user(group=User.Group.CLIENT.value, project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_progress_to_requesting_approval.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_contested_to_removed_by_client(self):
        client = self._get_user(group=User.Group.CLIENT.value, project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_removed.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/11/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 11, 'status': QualityIssue.Status.REMOVED})
        self.assertDatabaseHas(Subtask, {'pk': 16, 'status': Subtask.Status.REMOVED})
        self.assertDatabaseHas(Subtask, {'pk': 17, 'status': Subtask.Status.REMOVED})

    def test_transform_subtask_status_from_contested_to_removed_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_removed.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_under_review_to_removed_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_removed.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.REMOVED})

    def test_transform_subtask_status_from_under_review_to_removed_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_removed.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_under_inspection_to_requesting_approval_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_in_under_inspection_to_requesting_approval.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/13/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 13, 'status': QualityIssue.Status.REQUESTING_APPROVAL,
                                              'last_confirmed_update__comment': new_quality_issue_update['comment']})
        self.assertDatabaseHas(Subtask, {'pk': 19, 'status': Subtask.Status.REQUESTING_APPROVAL,
                                         'last_confirmed_update__comment': new_quality_issue_update['comment'],
                                         'last_confirmed_update__new_data__status': Subtask.Status.REQUESTING_APPROVAL})

    def test_transform_subtask_status_from_requesting_approval_to_requested_approval_rejected_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_requested_approval_rejected.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/7/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {
            'pk': 7,
            'status': QualityIssue.Status.REQUESTED_APPROVAL_REJECTED,
            'last_confirmed_update__comment': new_quality_issue_update['comment'],
            'last_confirmed_update__files__id__in': new_quality_issue_update['files']
        })
        self.assertDatabaseHas(Subtask, {
            'pk': 8,
            'status': Subtask.Status.REQUESTED_APPROVAL_REJECTED,
            'last_confirmed_update__comment': new_quality_issue_update['comment'],
            'last_confirmed_update__files__id__in': new_quality_issue_update['files']
        })
        self.assertDatabaseHas(Subtask, {
            'pk': 9,
            'status': Subtask.Status.REQUESTED_APPROVAL_REJECTED,
            'last_confirmed_update__comment': new_quality_issue_update['comment'],
            'last_confirmed_update__files__id__in': new_quality_issue_update['files']
        })

    def test_update_by_client_with_sending_message_to_subcontractor(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/update_by_clinet_with_sending_message_to_subcontractor.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_requesting_approval_to_requested_approval_rejected_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_requested_approval_rejected.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_contested_to_under_review_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_under_review.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {
            'pk': 1,
            'status': QualityIssue.Status.UNDER_REVIEW
        })

    def test_transform_subtask_status_from_contested_to_under_review_without_due_date(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_under_review.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/6/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_contested_to_under_review_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_contested_to_under_review.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.UNDER_REVIEW})

    def test_transform_subtask_status_from_requesting_approval_to_closed_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_closed_out.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.CLOSED})

    def test_transform_subtask_status_from_closed_to_requesting_approval_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_closed_out_to_requesting_approval.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.REQUESTING_APPROVAL})

    def test_transform_subtask_status_from_under_review_to_in_progress_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_in_progress.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.IN_PROGRESS})
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/quality_issue_reopened.html'
            },
        ])

    def test_transform_subtask_status_from_under_review_to_in_progress_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_in_progress.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_under_review_to_contested_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_contested.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_transform_subtask_status_from_under_review_to_contested_by_company_admin(self):
        client = self._get_user(project=self.WORKING_PROJECT, groups__in=[User.Group.COMPANY_ADMIN.value, User.Group.ADMIN.value, User.Group.MANAGER.value])
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_under_review_to_contested.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.CONTESTED,
                                              'last_confirmed_update__comment': new_quality_issue_update['comment']})

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/quality_issue_without_rework_contested_for_multiplex.html'
            },
        ])

    def test_transform_subtask_status_from_requested_approval_rejected_to_requesting_approval_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requested_approval_rejected_to_requesting_approval.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.REQUESTING_APPROVAL,
                                              'last_confirmed_update__comment': new_quality_issue_update['comment']})

    def test_transform_subtask_status_from_requested_approval_rejected_to_requesting_approval_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requested_approval_rejected_to_requesting_approval.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'last_confirmed_update': None,
                                              'status': QualityIssue.Status.REQUESTING_APPROVAL})
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/notify_quality_issue_owner_about_requesting_approval.html'
            },
        ])

    def test_transform_subtask_status_from_requesting_approval_to_in_progress_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_in_progress.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.IN_PROGRESS})

    def test_transform_subtask_status_from_requesting_approval_to_in_progress_by_client(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_in_progress.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/1/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_status_transition_from_requesting_approval_into_closed_by_multiplex(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_from_requesting_approval_into_closed.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/7/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 7, 'status': QualityIssue.Status.CLOSED})
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue': 7,
            'old_data': {'status': QualityIssue.Status.REQUESTING_APPROVAL},
            'new_data': {'status': QualityIssue.Status.CLOSED}
        })
        self.assertDatabaseHas(Subtask, {'pk': 8, 'status': Subtask.Status.CLOSED})
        self.assertDatabaseHas(Subtask, {'pk': 9, 'status': Subtask.Status.CLOSED})
        self.assertDatabaseHas(SubtaskUpdate, {
            'subtask': 8,
            'old_data': {'status': Subtask.Status.REQUESTING_APPROVAL},
            'new_data': {'status': Subtask.Status.CLOSED}
        })
        self.assertDatabaseHas(SubtaskUpdate, {
            'subtask': 9,
            'old_data': {'status': Subtask.Status.REQUESTING_APPROVAL},
            'new_data': {'status': Subtask.Status.CLOSED}
        })

    def test_update_due_date_in_invalid_status(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/update_quality_issue_due_date_in_invalid_status.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/8/updates/', new_quality_issue_update)

        self.assertBadRequest(response)

    def test_update_contested_without_status_changing(self):
        client = self._get_user(project=self.WORKING_PROJECT, group=User.Group.CLIENT.value)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/update_contested_quality_issue_without_status_changing.json')

        self.force_login_user(client.pk)
        response = self.client.post('/api/projects/5/quality-issues/6/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssueUpdate, {'old_data': {'status': QualityIssue.Status.CONTESTED},
                                                    'new_data': {'status': QualityIssue.Status.CONTESTED},
                                                    'comment': new_quality_issue_update['comment'],
                                                    'quality_issue': 6})

    def test_transform_subtask_status_from_requesting_approval_to_in_progress_with_last_confirmed_update_revert(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        new_quality_issue_update = self.load_request_fixture(
            '/quality_issue_updates/transform_quality_issue_status_from_requesting_approval_to_in_progress.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/quality-issues/10/updates/', new_quality_issue_update)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {
            'pk': 10,
            'status': QualityIssue.Status.IN_PROGRESS,
            'last_confirmed_update__comment': new_quality_issue_update['comment'],
            'last_confirmed_update__old_data__status': new_quality_issue_update['old_data']['status'],
            'last_confirmed_update__new_data__status': new_quality_issue_update['new_data']['status'],
        })

    def test_update_reopen_existing(self):
        multiplex_user = self._get_staff(project=self.WORKING_PROJECT)
        reopen_subtask = self.load_request_fixture('/quality_issue_updates/reopen_subtask.json')

        self.force_login_user(multiplex_user.pk)
        response = self.client.post('/api/projects/5/subtasks/18/updates/', reopen_subtask)

        self.assertCreated(response)
        self.assertDatabaseHas(QualityIssue, {'pk': 12, 'status': QualityIssue.Status.IN_PROGRESS})
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue': 12,
            'old_data': {'status': QualityIssue.Status.CLOSED},
            'new_data': {'status': QualityIssue.Status.IN_PROGRESS}
        })

    def get_project_user_for_comments_creation_from_forbidden_statuses(self):
        return (
            ({'group': User.Group.ADMIN, 'project': self.WORKING_PROJECT},),
            ({'group': User.Group.MANAGER, 'project': self.WORKING_PROJECT},),
            ({'group': User.Group.CLIENT, 'project': self.WORKING_PROJECT},),
        )

    def get_non_project_user_for_comments_creation_from_quality_with_subtask(self):
        return (
            ((Q(group=User.Group.CLIENT), ~Q(project=self.WORKING_PROJECT)),),
            ((Q(group=User.Group.CONSULTANT), ~Q(project=self.WORKING_PROJECT)),),
        )

    def get_non_project_user_for_comments_creation(self):
        return (
            ((Q(group=User.Group.ADMIN), ~Q(project=self.WORKING_PROJECT)),),
            ((Q(group=User.Group.MANAGER), ~Q(project=self.WORKING_PROJECT)),),
            ((Q(group=User.Group.CLIENT), ~Q(project=self.WORKING_PROJECT)),),
        )

    def test_create_comment_in_under_review_by_project_admin(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})
        user = self._get_admin(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_under_review_by_project_admin.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 1,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    def test_create_comment_in_under_review_by_project_manager(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})
        user = self._get_manager(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_under_review_by_project_manager.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 1,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    def test_create_comment_in_under_review_by_project_client(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})
        user = self._get_client(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_under_review_by_project_client.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 1,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    @data_provider(get_non_project_user_for_comments_creation)
    def test_create_comment_in_under_review_by_non_project_user(self, user_filters):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})

        self._log_in_as_user(*user_filters)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_create_comment_in_under_review_by_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_create_comment_in_under_review_by_non_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 1})

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_create_comment_in_contested_without_subtask_by_project_admin(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})
        user = self._get_admin(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_contested_by_project_admin.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 6,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    def test_create_comment_in_contested_without_subtask_by_project_manager(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})
        user = self._get_manager(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_contested_by_project_manager.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 6,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    def test_create_comment_in_contested_without_subtask_by_project_client(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})
        user = self._get_manager(project=self.WORKING_PROJECT)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_contested_by_project_client.json')
        self.assertDatabaseHas(QualityIssueUpdate, {
            'quality_issue_id': 6,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    @data_provider(get_non_project_user_for_comments_creation)
    def test_create_comment_in_contested_without_subtask_by_non_project_user(self, user_filters):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})

        self._log_in_as_user(*user_filters)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_create_comment_in_contested_without_subtask_by_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    def test_create_comment_in_contested_without_subtask_by_non_project_subcontractor(self):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 6})

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url, request_data)

        self.assertForbidden(response)

    @data_provider(get_project_user_for_comments_creation_from_forbidden_statuses)
    def test_create_comment_from_removed_quality_issue(self, user_filters):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 14})

        self._log_in_as_user(**user_filters)
        response = self.client.post(url, request_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You cannot create comment for quality issue in status closed or removed."]}')

    @data_provider(get_project_user_for_comments_creation_from_forbidden_statuses)
    def test_create_comment_from_closed_quality_issue(self, user_filters):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 3})

        self._log_in_as_user(**user_filters)
        response = self.client.post(url, request_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You cannot create comment for quality issue in status closed or removed."]}')

    @freeze_time("2022-01-14 00:00:00")
    def test_create_and_copy_comment_to_associated_subtask_by_project_client(self):
        quality_issue_pk = 2
        qi_before_update = QualityIssue.objects.filter(pk=quality_issue_pk).get()
        subtask_before_update = qi_before_update.subtask_set.first()
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT,
                                                           'quality_issue_pk': quality_issue_pk})

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_quality_issue_with_subtask_by_project_client.json')

        qi_after_update = QualityIssue.objects.filter(pk=quality_issue_pk).get()
        subtask_after_update = qi_after_update.subtask_set.first()
        self.assertNotEquals(qi_before_update.updated_at, qi_after_update.updated_at)
        self.assertNotEquals(subtask_before_update.updated_at, subtask_after_update.updated_at)

        self.assertDatabaseHas(QualityIssueUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'quality_issue': quality_issue_pk,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertEmailEquals([
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Rework & Defect Statused - Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/comment_created_by_client.html'
            },
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/subtask_comment_sync_create_by_client.html'
            },
            {
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/comment_created_for_recipients_by_client.html'
            }
        ])

    @freeze_time("2022-01-14 00:00:00")
    def test_create_and_copy_comment_to_associated_subtask_by_project_consultant(self):
        quality_issue_pk = 2
        qi_before_update = QualityIssue.objects.filter(pk=quality_issue_pk).get()
        subtask_before_update = qi_before_update.subtask_set.first()
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT,
                                                           'quality_issue_pk': quality_issue_pk})

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/quality_issue_update/create_comment_for_quality_issue_with_subtask_by_project_consultant.json')

        qi_after_update = QualityIssue.objects.filter(pk=quality_issue_pk).get()
        subtask_after_update = qi_after_update.subtask_set.first()
        self.assertNotEquals(qi_before_update.updated_at, qi_after_update.updated_at)
        self.assertNotEquals(subtask_before_update.updated_at, subtask_after_update.updated_at)

        self.assertDatabaseHas(QualityIssueUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'quality_issue': quality_issue_pk,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertEmailEquals([
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Rework & Defect Statused - Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/comment_created_by_consultant.html'
            },
            {
                'to': ['cool.brad@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/subtask_comment_sync_create_by_consultant.html'
            },
            {
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'subject': 'MBuild – Urgent Attention, Immediate Response Required – Project 5, Building A - A - Hall',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/quality_issue_update/comment_created_for_recipients_by_consultant.html'
            }
        ])

    @data_provider(get_non_project_user_for_comments_creation_from_quality_with_subtask)
    def test_create_and_copy_comment_to_associated_subtask_by_non_project_user(self, user_filters: list):
        request_data = self.load_request_fixture('/quality_issue_updates/add_comment.json')
        url = reverse('quality_issue_update_list', kwargs={'project_pk': self.WORKING_PROJECT, 'quality_issue_pk': 2})

        self._log_in_as_user(*user_filters)
        response = self.client.post(url, request_data)

        self.assertForbidden(response)
        self.assertEquals(response.content, b'{"detail":"You do not have permission to perform this action."}')
