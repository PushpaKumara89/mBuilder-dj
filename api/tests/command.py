from django.core.management import call_command

from api.enums.entities import Entities
from api.models import Command, Subtask, SubtaskUpdate, Task, Event, TaskUpdate, QualityIssueUpdate, QualityIssue
from api.tests.test import TransactionTestCase


class CommandTest(TransactionTestCase):
    mongo_fixtures = ['api/tests/fixtures/dumps/mongo/command.json']
    fixtures = ['api/tests/fixtures/dumps/command.json']

    def test_create_by_staff(self):
        data = self.load_request_fixture('/commands/create_commands.json')
        project_staff = self._get_staff(project=1)

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/create_commands_assertion_by_staff.json')

    def test_create_by_superuser(self):
        data = self.load_request_fixture('/commands/create_commands.json')
        project_staff = self._get_superuser()

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/create_commands_assertion_by_superuser.json')

    def test_create_with_all_local_entities_by_superuser(self):
        data = self.load_request_fixture('/commands/create_all_local_entities.json')
        project_staff = self._get_superuser()

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/create_commands_all_local_entities_assertion.json')

        self.assertDatabaseHas(Subtask, {'pk': 21, 'description': 'updated description'})

    def test_delete_with_all_local_entities_by_superuser(self):
        data = self.load_request_fixture('/commands/delete_all_local_entities.json')
        project_staff = self._get_superuser()

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/delete_commands_all_local_entities_assertion.json')

        self.assertSoftDeleted(Subtask, {'local_id': 'BUIF737382323'})

    def test_restore_with_all_local_entities_by_superuser(self):
        data = self.load_request_fixture('/commands/restore_all_local_entities.json')
        project_staff = self._get_superuser()

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/restore_commands_all_local_entities_assertion.json')

        self.assertTrue(Command.objects(
            data__parent_entity_local_id='BUIF737382323',
            status=Command.Statuses.PROCESSED.value,
            type=Command.Types.RESTORE_ENTITY.value
        ).count() == 1)
        self.assertDatabaseHas(Subtask, {'local_id': 'BUIF737382323'})

    def test_unauthorized_create(self):
        data = self.load_request_fixture('/commands/create_commands.json')
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertUnauthorized(response)

    def test_process_commands(self):
        call_command('process_commands')

        # Assert creation from events.
        self.assertTrue(Command.objects(data__comment='new subtask update from event',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertTrue(Command.objects(data__comment='new conflicted subtask update from event',
                                        status=Command.Statuses.CONFLICTED.value))
        self.assertDatabaseHas(SubtaskUpdate, {'comment': 'new conflicted subtask update from event',
                                               'is_conflict': True, 'subtask': 1})
        self.assertTrue(Command.objects(data__local_id='werg234twef34', status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(Task, {'package_activity': 3, 'package_activity_task': 4,
                                      'location_matrix': 1, 'local_id': 'werg234twef34'})
        self.assertTrue(Event.objects(type=Event.Types.ENTITY_CREATED.value, entity=Entities.TASK.value,
                                      project_id=5, data__local_id='werg234twef34'))
        # Assert update from events.
        self.assertTrue(Command.objects(data__description='successfully updated subtask',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(Subtask, {'pk': 1, 'description': 'successfully updated subtask'})

        # Assert delete from events.
        self.assertTrue(Command.objects(data__description='successfully deleted subtask',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseMissing(Subtask, 2)

        # Assert restore from events.
        self.assertTrue(Command.objects(data__description='successfully restore subtask',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(Subtask, 3)

        # Assert that related to new subtask entities get respective local id
        self.assertTrue(Command.objects(data__local_id='jimmyneutron222',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(Subtask, {'local_id': 'jimmyneutron222'})
        self.assertDatabaseHas(SubtaskUpdate, {'local_id': 'familyguy333'})
        self.assertDatabaseHas(TaskUpdate, {'local_id': 'simpsons444'})

        # Assert that related to new quality issue update entities get respective local id
        # todo Resolve this case.
        # self.assertTrue(Command.objects(data__local_id='messi998',
        #                                 status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(SubtaskUpdate, {'local_id': 'pinocchio555'})
        self.assertDatabaseHas(QualityIssueUpdate, {'local_id': 'messi998'})

        # Assert that quality issue comment create with related subtask update
        list(Command.objects(data__local_id='prettyenvy',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertTrue(Command.objects(data__local_id='prettyenvy',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(QualityIssueUpdate, {'local_id': 'prettyenvy', 'is_comment': True})
        self.assertDatabaseHas(SubtaskUpdate, {'local_id': 'stounhange', 'is_comment': True})

        # Assert that subtask comment created with related quality issue update
        self.assertTrue(Command.objects(data__local_id='123456qwerty',
                                        status=Command.Statuses.PROCESSED.value))
        self.assertDatabaseHas(SubtaskUpdate, {'local_id': '123456qwerty', 'is_comment': True})
        self.assertDatabaseHas(QualityIssueUpdate, {'local_id': 'pinkyandbrain', 'is_comment': True})

        # Assert conflicted subtask update is synced but do not update related quality issue.
        self.assertDatabaseHas(SubtaskUpdate, {'local_id': '123457qwerty', 'is_comment': False,
                                              'is_conflict': True, 'subtask': 7})
        self.assertDatabaseHas(Subtask, {'pk': 7, 'status': 'in_progress'})
        self.assertDatabaseHas(QualityIssueUpdate, {'local_id': 'pinkyandbrain', 'is_comment': False,
                                                   'is_conflict': True, 'quality_issue': 9})
        self.assertDatabaseHas(QualityIssue, {'pk': 9, 'status': 'under_review'})

        self.assertEventsExist('/command/process_commands_events_assertion.json')

    def __remove_id_from_response_data(self, response):
        for key, r in enumerate(response.data):
            del response.data[key]['id']

    def test_change_subtask_task(self):
        data = self.load_request_fixture('/commands/change_subtask_task.json')
        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/1/commands/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/command/change_subtask_task.json')

        self.assertTrue(Command.objects(status=Command.Statuses.CONFLICTED.value,
                                        related_entities_local_ids__old_task_update_local_id='ivandrago777'))
        # Check that conflicted subtask update didn't apply.
        self.assertDatabaseHas(Subtask, {'pk': 6, 'status': Subtask.Status.CLOSED})
        self.assertDatabaseHas(SubtaskUpdate, {'subtask__pk': 6, 'old_data__status': Subtask.Status.CONTESTED,
                                               'new_data__status': Subtask.Status.CONTESTED, 'is_conflict': True})
        self.assertDatabaseHas(Task, {'pk': 3, 'status': Task.Statuses.OUTSTANDING})
        self.assertDatabaseHas(TaskUpdate, {'task__pk': 3, 'new_data__status': Task.Statuses.OUTSTANDING,
                                            'old_data__status': Task.Statuses.REJECTED, 'local_id': 'ivandrago777'})

    def test_list_commands_as_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')

    def test_list_commands_as_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')

    def test_list_commands_as_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')

    def test_list_commands_as_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')

    def test_list_commands_as_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')

    def test_list_commands_as_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/commands/', {
            'local_id': [
                '34ff34rsadf',
                'werg234twef34',
                'jimmyneutron222'
            ]
        })

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/command/search_commands.json')
