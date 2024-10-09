from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import SubtaskUpdate, Subtask, QualityIssue, QualityIssueUpdate, User
from api.tests.test import TestCase, data_provider


class SubtaskUpdateTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/subtasks_updates.json']
    WORKING_PROJECT = 5

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        del new_subtask_update['files']
        del new_subtask_update['recipients']

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 1, 'status': Subtask.Status.IN_PROGRESS, 'user__pk': 2})
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/subtask_completed.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com', 'cool.subcontractor@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/created_based_on_quality_issue_recipients.html'
            }
        ])
        self.assertEventsExist('/subtasks_updates/create_events_assertion.json')

    def test_create_with_company_not_from_white_list(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update.json')
        new_subtask_update['new_data']['company'] = 1

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"company":["You should select only companies that assigned on package activities."]}')

    def test_create_with_unknown_field(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update.json')
        new_subtask_update['new_data']['unknown_field'] = 123

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["Got unknown fields: {\'unknown_field\'}"]}')

    def test_create_by_subtask_assigned_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_by_subcontractor.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        del new_subtask_update['files']
        del new_subtask_update['recipients']

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 1, 'status': Subtask.Status.DECLINED, 'user__pk': 2})
        self.assertEventsExist('/subtasks_updates/create_by_subcontractor_events_assertion.json')

    def test_forbid_create_by_subtask_unassigned_subcontractor(self):
        subcontractor = self._get_user(~Q(company__in=[2, 3]), groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_by_subcontractor.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertForbidden(response)

    def test_create_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_by_subcontractor.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertCreated(response)

    def test_forbid_create_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_by_subcontractor.json')

        self.force_login_user(non_project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_by_subcontractor.json')
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertUnauthorized(response)

    def test_update_subtask_in_contested_status(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_for_in_contested_subtask.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        del new_subtask_update['files']
        del new_subtask_update['recipients']

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 8, 'status': Subtask.Status.IN_PROGRESS, 'user__pk': 2, 'task': 2,
                                         'description': 'Tik-Tok', 'estimation': 22, 'due_date': "2020-02-02"})

    def test_transform_from_in_progress_to_declined_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_update_by_subcontractor_from_in_progress_to_declined.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/7/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 7, 'status': Subtask.Status.DECLINED, 'user__pk': 2})
        # Check that decline reason with files didn't copy to related quality issue.
        self.assertDatabaseHas(QualityIssueUpdate, {'quality_issue': 9, 'new_data__status': Subtask.Status.DECLINED,
                                                    'comment': None, 'files': None})

    def test_update_declined_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_declined_by_subcontractor.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/9/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 9, 'status': Subtask.Status.DECLINED, 'user__pk': 2})

    def test_transform_from_in_progress_to_under_inspection_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_subcontractor_in_progress_to_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/7/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 7, 'status': Subtask.Status.UNDER_INSPECTION, 'user__pk': 2})
        # Check that approval reason with files didn't copy to related quality issue.
        self.assertDatabaseHas(QualityIssueUpdate, {'quality_issue': 9, 'comment': None, 'files': None,
                                                    'new_data__status': Subtask.Status.UNDER_INSPECTION})

    def test_update_under_inspection_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_subcontractor_update_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.UNDER_INSPECTION, 'user__pk': 2})

    def test_undo_by_subcontractor_from_declined_to_in_progress(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_declined_to_in_progress.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/9/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 9, 'status': Subtask.Status.IN_PROGRESS,
                                         'user__pk': 2, 'last_confirmed_update': None})

    def test_transform_from_under_inspection_to_in_progress_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_subcontractor_under_inspection_to_in_progress.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.IN_PROGRESS, 'user__pk': 2})

    def test_transform_from_inspection_rejected_to_contested_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_subcontractor_inspection_rejected_to_contested.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.CONTESTED, 'user__pk': 2})
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/send_email_about_contested_subtask.html'
            }
        ])

    def test_transform_from_inspection_rejected_to_under_inspection_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_subcontractor_inspection_rejected_to_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, new_subtask_update)
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.UNDER_INSPECTION, 'user__pk': 2})
        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/send_email_about_requesting_approval_subtask.html'
            }
        ])

    def test_create_with_files(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_with_files.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertCreated(response)

        subtask_update = SubtaskUpdate.objects.filter(pk=response.data['id']).get()
        self.assertTrue(subtask_update.files.filter(pk__in=[1, 2]).exists())
        self.assertEventsExist('/subtasks_updates/create_with_files_events_assertion.json')

    def test_forbid_create_by_subcontractor(self):
        subcontractor = self._get_user(~Q(company=8), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)

        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update.json')
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertForbidden(response)

    def test_create_incorrect_new_data(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/new_subtask_update_incorrect_new_data.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_create_incorrect_new_data_incorrect_field(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/new_subtask_update_incorrect_new_data_incorrect_field.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/get_subtask_update.json')

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/get_subtask_update.json')

    def test_forbid_get_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertForbidden(response)

    def test_get_by_subtask_by_its_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/get_subtask_update_by_its_subcontractor.json')

    def test_forbid_get_by_subtask_by_unassigned_subcontractor(self):
        subcontractor = self._get_user(~Q(company__in=[2, 3]), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertForbidden(response)

    def test_unauthenticated_get(self):
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/')

        self.assertUnauthorized(response)

    def test_get_with_expandable_fields(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/1/', {'expand': ['expanded_subtask',
                                                                                        'expanded_user',
                                                                                        'expanded_files',
                                                                                        'expanded_recipients']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/get_subtask_update_with_expandable_fields.json')

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/subtasks/1/updates/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(SubtaskUpdate, 1)
        self.assertEventsExist('/subtasks_updates/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/projects/5/subtasks/1/updates/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/subtasks/1/updates/1/')

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'created_at'},
                '/subtasks_updates/get_all_sorted_by_created_at.json'
            ),
            (
                {'all': True, 'sort': '-created_at'},
                '/subtasks_updates/get_all_sorted_by_created_at_desc.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/', {'all': 1})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_subtask_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/', {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/get_all_by_subtask_subcontractor.json')

    def test_forbid_search_by_subtask_unassigned_subcontractor(self):
        subcontractor = self._get_user(~Q(company=3), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/5/subtasks/1/updates/', {'all': True})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/subtasks/1/updates/', {'all': True})

        self.assertUnauthorized(response)

    def test_re_open_subtask_from_closed(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/re_open_subtask_from_closed.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/4/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 4, 'status': Subtask.Status.IN_PROGRESS})
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.IN_PROGRESS})

    def test_forbid_re_open_subtask_from_closed(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/re_open_subtask_from_closed.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/4/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_re_open_subtask_from_removed(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/re_open_subtask_from_removed.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/3/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_forbid_re_open_subtask_from_removed(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/re_open_subtask_from_removed.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/3/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_re_open_subtask_from_contested(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture('/subtasks_updates/re_open_subtask_from_contested.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 8, 'status': Subtask.Status.IN_PROGRESS})
        self.assertDatabaseHas(QualityIssue, {'pk': 1, 'status': QualityIssue.Status.IN_PROGRESS})

    def test_re_open_subtask_from_requesting_approval(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/re_open_subtask_from_requesting_approval.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/15/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 15, 'status': Subtask.Status.IN_PROGRESS,
                                         'last_confirmed_update__comment': new_subtask_update['comment'],
                                         'last_confirmed_update__old_data__status': new_subtask_update['old_data']['status'],
                                         'last_confirmed_update__new_data__status': new_subtask_update['new_data']['status']})
        self.assertDatabaseHas(QualityIssue, {'pk': 5, 'status': QualityIssue.Status.IN_PROGRESS})

    def test_undo_subtask_from_under_inspection_to_in_progress_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_in_progress.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.IN_PROGRESS})

    def test_change_subtask_status_from_under_inspection_to_in_progress_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_in_progress.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_undo_subtask_from_in_progress_to_contested_by_multiplex(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_in_progress_to_contested.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 1, 'status': Subtask.Status.CONTESTED})

    def test_reject_subtask_from_inspection_rejected_to_contested_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_inspection_rejected_to_contested.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.CONTESTED})

    def test_reject_subtask_from_inspection_rejected_to_contested_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_inspection_rejected_to_contested.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_undo_subtask_from_inspection_rejected_to_under_inspection_by_multiplex(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_inspection_rejected_to_under_inspection.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.UNDER_INSPECTION})

    def test_close_out_subtask_from_inspection_rejected_to_under_inspection_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_inspection_rejected_to_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/11/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 11, 'status': Subtask.Status.UNDER_INSPECTION})
        self.assertDatabaseHas(QualityIssue, {'pk': 2, 'status': QualityIssue.Status.UNDER_INSPECTION})

    def test_close_out_subtask_from_in_progress_to_under_inspection_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_in_progress_to_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 1, 'status': Subtask.Status.UNDER_INSPECTION})
        self.assertDatabaseHas(QualityIssue, {'pk': 2, 'status': QualityIssue.Status.UNDER_INSPECTION})

    def test_change_subtask_from_in_progress_to_under_inspection_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_in_progress_to_under_inspection.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_remove_subtask_from_contested_to_removed_by_multiplex(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_contested_to_removed.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 8, 'status': Subtask.Status.REMOVED})

    def test_change_subtask_from_contested_to_removed_by_subcontractor(self):
        subcontractor = self._get_user(company=2, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_contested_to_removed.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_reject_subtask_from_under_inspection_to_inspection_reject_by_multiplex(self):
        superuser = self._get_superuser()
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_inspection_rejected.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.INSPECTION_REJECTED})
        # Check that rejection reason with photo didn't copy to related quality issue.
        self.assertDatabaseHas(QualityIssueUpdate, {'quality_issue': 3, 'comment': None, 'files': None,
                                                    'new_data__status': Subtask.Status.INSPECTION_REJECTED})

    def test_change_subtask_from_under_inspection_to_inspection_reject_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_inspection_rejected.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_update_subtask_while_in_progress_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/update_subtask_while_in_progress.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/7/updates/', new_subtask_update)

        assertion_data = new_subtask_update['new_data']
        del assertion_data['files']

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 7, **assertion_data})

    def test_request_approval_subtask_by_multiplex_with_transfer_quality_issue_into_requesting_approval(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_requesting_approval.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 10, 'status': Subtask.Status.REQUESTING_APPROVAL,
                                         'last_confirmed_update__comment': new_subtask_update['comment'],
                                         'last_confirmed_update__old_data__status': new_subtask_update['old_data']['status'],
                                         'last_confirmed_update__new_data__status': new_subtask_update['new_data']['status']})
        self.assertDatabaseHas(QualityIssue, {'pk': 3, 'status': QualityIssue.Status.REQUESTING_APPROVAL})

    def test_request_approval_subtask_by_subcontractor(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_under_inspection_to_requesting_approval.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/10/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_undo_approval_subtask_by_multiplex_with_transfer_quality_issue_into_in_progress(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_to_under_inspection.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/17/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 17, 'status': Subtask.Status.UNDER_INSPECTION})
        self.assertDatabaseHas(QualityIssue, {'pk': 6, 'status': QualityIssue.Status.UNDER_INSPECTION})

    def test_undo_approval_subtask_by_subcontractor_with_transfer_quality_issue_into_in_progress(self):
        subcontractor = self._get_user(company=3, groups=User.Group.SUBCONTRACTOR.value)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_to_under_inspection.json')

        self.force_login_user(subcontractor.pk)
        response = self.client.post('/api/projects/5/subtasks/17/updates/', new_subtask_update)

        self.assertBadRequest(response)

    def test_update_location_matrix(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/update_subtask_location.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/1/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'comment': 'new test comment',
                                               'old_data': {'status': Subtask.Status.IN_PROGRESS, 'task': 2},
                                               'new_data': {'status': Subtask.Status.IN_PROGRESS, 'task': 4},
                                               'subtask': 1,
                                               'user': 2})
        self.assertDatabaseHas(QualityIssueUpdate,
                               {'old_data': {'location_matrix': 1, 'status': QualityIssue.Status.IN_PROGRESS},
                                'new_data': {'location_matrix': 2, 'status': QualityIssue.Status.IN_PROGRESS},
                                'quality_issue': 2,
                                'user': 2})
        self.assertDatabaseMissing(QualityIssue, {'pk': 2, 'location_matrix': 1})
        self.assertDatabaseHas(QualityIssue, {'pk': 2, 'location_matrix': 2})

    def test_update_approval_reason_for_requesting_approval(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture('/subtasks_updates/update_approval_evidence.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/18/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate,
                               {'old_data': {'status': Subtask.Status.REQUESTING_APPROVAL},
                                'new_data': {'status': Subtask.Status.REQUESTING_APPROVAL},
                                'subtask': 18,
                                'comment': new_subtask_update['comment'],
                                'user': 2})
        self.assertDatabaseHas(Subtask,
                               {'pk': 18,
                                'last_confirmed_update__comment': new_subtask_update['comment'],
                                'last_confirmed_update__new_data__status': Subtask.Status.REQUESTING_APPROVAL,
                                'last_confirmed_update__old_data__status': Subtask.Status.REQUESTING_APPROVAL})

    def test_undo_approval_subtask_by_multiplex_with_revert_last_confirmed_update_to_previous(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_to_under_inspection.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/19/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'pk': 19, 'status': Subtask.Status.UNDER_INSPECTION, 'last_confirmed_update': 7})
        self.assertDatabaseHas(QualityIssue, {'pk': 3, 'status': QualityIssue.Status.UNDER_INSPECTION})

    def test_transfer_subtask_from_in_progress_to_declined_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_in_progress_to_declined.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/7/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 7, **{field_name: value
                                                                for field_name, value in new_subtask_update.items()
                                                                if field_name != 'files'}})
        self.assertDatabaseHas(Subtask, {'id': 7, 'status': Subtask.Status.DECLINED})
        # Check that comment and files didn't copy.
        self.assertDatabaseHas(QualityIssueUpdate, {'quality_issue': 9, 'new_data__status': QualityIssue.Status.DECLINED,
                                                    'comment': None, 'files': None})

    def test_transfer_subtask_from_contested_to_declined_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_contested_to_declined.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 8, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 8, 'status': Subtask.Status.DECLINED})

    def test_transfer_subtask_from_requesting_approval_to_requesting_approval_rejected_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_to_requesting_approval_rejected.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 8, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 8, 'status': Subtask.Status.REQUESTED_APPROVAL_REJECTED})

    def test_transfer_subtask_from_requested_approval_rejected_to_in_progress_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_rejected_to_in_progress.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/8/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 8, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 8, 'status': Subtask.Status.IN_PROGRESS})

    def test_transfer_subtask_from_requested_approval_rejected_to_requesting_approval_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_requesting_approval_rejected_to_requesting_approval.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/20/updates/', new_subtask_update)

        del new_subtask_update['files']

        self.assertCreated(response)
        self.assertDatabaseHas(Subtask, {'id': 20, 'status': Subtask.Status.REQUESTING_APPROVAL})
        self.assertDatabaseHas(QualityIssue, {'id': 10, 'status': QualityIssue.Status.REQUESTING_APPROVAL})
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 20, **new_subtask_update})

    def test_transfer_subtask_from_declined_to_contested_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_declined_to_contested.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/9/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 9, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 9, 'status': Subtask.Status.CONTESTED})

    def test_transfer_subtask_from_declined_to_in_progress_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_declined_to_in_progress.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/9/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 9, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 9, 'status': Subtask.Status.IN_PROGRESS})

    def test_transfer_subtask_from_declined_to_removed_by_multiplex(self):
        project_staff = self._get_staff(project=5)
        new_subtask_update = self.load_request_fixture(
            '/subtasks_updates/transfer_subtask_from_declined_to_removed.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/subtasks/9/updates/', new_subtask_update)

        self.assertCreated(response)
        self.assertDatabaseHas(SubtaskUpdate, {'subtask': 9, **new_subtask_update})
        self.assertDatabaseHas(Subtask, {'id': 9, 'status': Subtask.Status.REMOVED})

    def get_project_users_for_comments_creation(self):
        return (
            ({'group': User.Group.ADMIN, 'project': self.WORKING_PROJECT}, '/quality_issue_update/create_comment_by_project_admin.json'),
            ({'group': User.Group.MANAGER, 'project': self.WORKING_PROJECT}, '/quality_issue_update/create_comment_by_project_manager.json'),
            ({'group': User.Group.SUBCONTRACTOR, 'project': self.WORKING_PROJECT}, '/quality_issue_update/create_comment_by_project_subcontractor.json'),
        )

    def get_project_user_for_comments_creation_from_forbidden_statuses(self):
        return (
            ({'group': User.Group.ADMIN, 'project': self.WORKING_PROJECT},),
            ({'group': User.Group.MANAGER, 'project': self.WORKING_PROJECT},),
            ({'group': User.Group.SUBCONTRACTOR, 'project': self.WORKING_PROJECT},),
        )

    def get_project_user_for_comments_creation_from_subtask_with_quality_issue(self):
        return (
            ({'group': User.Group.ADMIN, 'project': self.WORKING_PROJECT}, '/subtasks_updates/create_comment_for_quality_issue_with_subtask_by_project_admin.json'),
            ({'group': User.Group.MANAGER, 'project': self.WORKING_PROJECT}, '/subtasks_updates/create_comment_for_quality_issue_with_subtask_by_project_manager.json'),
        )

    @data_provider(get_project_users_for_comments_creation)
    def test_create_comment_by_project_user(self, user_filters, response_fixture):
        subtask_pk = 1
        request_data = self.load_request_fixture('/subtasks_updates/add_comment.json')
        url = reverse('subtasks_updates_list', kwargs={'project_pk': self.WORKING_PROJECT, 'subtask_pk': subtask_pk})
        user = self._get_user(**user_filters)

        self.force_login_user(user.pk)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, response_fixture)
        self.assertDatabaseHas(SubtaskUpdate, {
            'subtask': subtask_pk,
            'new_data': {},
            'old_data': {},
            'is_comment': True,
            'comment': request_data['comment'],
            'user': user.pk
        })

    @data_provider(get_project_user_for_comments_creation_from_forbidden_statuses)
    def test_create_comment_from_removed_subtask(self, user_filters):
        request_data = self.load_request_fixture('/subtasks_updates/add_comment.json')
        url = reverse('subtasks_updates_list', kwargs={'project_pk': self.WORKING_PROJECT, 'subtask_pk': 3})

        self._log_in_as_user(**user_filters)
        response = self.client.post(url, request_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You cannot create comment for quality issue in status closed or removed."]}')

    @data_provider(get_project_user_for_comments_creation_from_forbidden_statuses)
    def test_create_comment_from_closed_subtask(self, user_filters):
        request_data = self.load_request_fixture('/subtasks_updates/add_comment.json')
        url = reverse('subtasks_updates_list', kwargs={'project_pk': self.WORKING_PROJECT, 'subtask_pk': 4})

        self._log_in_as_user(**user_filters)
        response = self.client.post(url, request_data)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["You cannot create comment for quality issue in status closed or removed."]}')

    @data_provider(get_project_user_for_comments_creation_from_subtask_with_quality_issue)
    def test_create_and_copy_comment_to_associated_quality_issue_by_project_user(self, user_filters, fixture):
        subtask_pk = 10
        request_data = self.load_request_fixture('/subtasks_updates/add_comment.json')
        url = reverse('subtasks_updates_list', kwargs={'project_pk': self.WORKING_PROJECT, 'subtask_pk': subtask_pk})

        self._log_in_as_user(**user_filters)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, fixture)

        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'subtask': subtask_pk,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertDatabaseHas(QualityIssueUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        self.assertEmailEquals([
            {
                'subject': 'MBuild – Rework & Defect Statused – Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/comment_created_multiplex.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['cool.brad@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/quality_issue_sync_create.html'
            },
            {
                'subject': 'MBuild – Urgent Attention, Immediate Response Required - Project 5, Building A - A - Hall',
                'to': ['tom_dvaer@gmail.com', 'tim_robinson@gmail.com'],
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'fixture': self.responses_fixtures_dir + '/subtasks_updates/quality_issue_sync_create_for_recipients.html'
            }
        ])

    def test_create_and_copy_comment_to_associated_quality_issue_by_project_subcontractor(self):
        subtask_pk = 1
        request_data = self.load_request_fixture('/subtasks_updates/add_comment.json')
        url = reverse('subtasks_updates_list', kwargs={'project_pk': self.WORKING_PROJECT, 'subtask_pk': subtask_pk})

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url, request_data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/subtasks_updates/create_comment_for_quality_issue_with_subtask_by_project_subcontractor.json')

        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'subtask': subtask_pk,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })

        # Make sure that comments didn't copy by subcontractor.
        self.assertDatabaseMissing(QualityIssueUpdate, {
            'comment': request_data['comment'],
            'is_comment': True,
            'old_data': {},
            'new_data': {},
            'files__id__in': request_data['files']
        })
