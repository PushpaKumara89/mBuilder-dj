import logging
import uuid

import sentry_sdk
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from safedelete.models import is_safedelete_cls
from sentry_sdk import capture_exception

from api.enums.entities import Entities
from api.http.serializers import SubtaskSerializer, QualityIssueSerializer, UserSerializer, SubtaskUpdateSerializer, \
    QualityIssueUpdateSerializer
from api.http.serializers.task.task_create_serializer import TaskCreateSerializer
from api.http.serializers.task_update.task_update_serializer import TaskUpdateSerializer
from api.models import Subtask, SubtaskUpdate, QualityIssue, QualityIssueUpdate, User, Task, TaskUpdate, \
    Command as CommandModel
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService
from api.services.subtask_entity_service import SubtaskEntityService
from api.services.subtask_update_entity_service import SubtaskUpdateEntityService
from api.services.task_entity_service import TaskEntityService
from api.services.task_update_entity_service import TaskUpdateEntityService
from api.utilities.helpers import Request


class CommandEntityProcessObject(object):
    def __init__(self, model, serializer, handler=None, use_command_in_handler=False, parent_entity=None):
        self.model = model
        self.serializer = serializer
        self.handler = handler
        self.use_command_in_handler = use_command_in_handler
        self.parent_entity = parent_entity


logger = logging.getLogger(__name__)
command_entities_process_objects = {
    Entities.USER.value: CommandEntityProcessObject(
        model=User,
        serializer=UserSerializer
    ),
    Entities.TASK.value: CommandEntityProcessObject(
        model=Task,
        serializer=TaskCreateSerializer,
        handler=TaskEntityService
    ),
    Entities.TASK_UPDATE.value: CommandEntityProcessObject(
        model=TaskUpdate,
        serializer=TaskUpdateSerializer,
        handler=TaskUpdateEntityService,
        use_command_in_handler=True,
        parent_entity=Entities.TASK.value
    ),
    Entities.SUBTASK.value: CommandEntityProcessObject(
        model=Subtask,
        serializer=SubtaskSerializer,
        handler=SubtaskEntityService
    ),
    Entities.SUBTASK_UPDATE.value: CommandEntityProcessObject(
        model=SubtaskUpdate,
        serializer=SubtaskUpdateSerializer,
        handler=SubtaskUpdateEntityService,
        use_command_in_handler=True,
        parent_entity=Entities.SUBTASK.value
    ),
    Entities.QUALITY_ISSUE.value: CommandEntityProcessObject(
        model=QualityIssue,
        serializer=QualityIssueSerializer,
        handler=QualityIssueEntityService
    ),
    Entities.QUALITY_ISSUE_UPDATE.value: CommandEntityProcessObject(
        QualityIssueUpdate,
        use_command_in_handler=True,
        handler=QualityIssueUpdateEntityService,
        serializer=QualityIssueUpdateSerializer,
        parent_entity=Entities.QUALITY_ISSUE.value
    ),
}


def process_commands(commands: list):
    for command in commands:
        with transaction.atomic():

            if command.is_entity_create:
                create_entity(command)
            elif command.is_entity_update:
                update_entity(command)
            elif command.is_entity_delete:
                delete_entity(command)
            elif command.is_entity_restore:
                restore_entity(command)

            if not command.is_failed and not command.is_conflicted:
                command.mark_as_processed()


def validate(serializer, command: CommandModel):
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        capture_fail(e, CommandModel.FailReason.VALIDATION_ERROR, command)
    except BaseException as e:
        capture_fail(e, CommandModel.FailReason.INTERNAL_ERROR, command)


def perform_action(callback: callable, command: CommandModel):
    try:
        callback()
    except BaseException as e:
        capture_fail(e, CommandModel.FailReason.INTERNAL_ERROR, command)


def create_entity(command: CommandModel):
    def has_reference_to_local_parent_entity():
        return command.data.get('parent_entity_local_id') is not None

    def parent_entity_missing_in_data():
        return not command.data.get(command_process_object.parent_entity)

    command_process_object = command_entities_process_objects.get(command.entity)
    if not command_process_object:
        logger.error('Invalid entity')
        command.failed_by_invalid_entity()
        return

    command.data['user'] = command.user

    if has_reference_to_local_parent_entity() and parent_entity_missing_in_data():
        parent_command_process_object = command_entities_process_objects.get(
            command_process_object.parent_entity
        )
        parent_entity = parent_command_process_object.model.objects.filter(
            local_id=command.data['parent_entity_local_id']
        ).first()

        if not parent_entity:
            logger.error('Missed parent entity')
            command.failed_by_missed_parent_entity()
            return

        command.data[command_process_object.parent_entity] = parent_entity.pk

    user = User.all_objects.filter(pk=command.user).get()
    serializer_context = {
        'data': command.data,
        'context': {
            'request': Request(user, []),
            'project_pk': command.project_id
        },
    }

    handler_context = {}
    if command_process_object.handler:
        handler_context = {
            'user': serializer_context['context']['request'].user,
            'project_pk': serializer_context['context']['project_pk']
        }
        if command_process_object.use_command_in_handler:
            handler_context['command'] = command

        if 'related_entities_local_ids' in command:
            handler_context.update(**command.related_entities_local_ids)

    serializer = command_process_object.serializer(**serializer_context)
    validate(serializer, command)
    if command.is_failed:
        return

    perform_creation(command_process_object, serializer, serializer_context, handler_context, command)


def perform_creation(command_process_object, serializer, serializer_context: dict, handler_context: dict, command: CommandModel):
    try:
        if command_process_object.handler:
            command_process_object.handler().create(serializer.validated_data, **handler_context)
        else:
            serializer(**serializer_context).create(serializer.validated_data)
    except BaseException as e:
        capture_fail(e, CommandModel.FailReason.INTERNAL_ERROR, command)


def perform_update(instance, command_process_object, serializer, serializer_context: dict, handler_context: dict, command: CommandModel):
    try:
        if command_process_object.handler:
            command_process_object.handler().update(instance, serializer.validated_data, **handler_context)
        else:
            serializer(**serializer_context).update(instance, serializer.validated_data)
    except BaseException as e:
        capture_fail(e, CommandModel.FailReason.INTERNAL_ERROR, command)


def update_entity(command: CommandModel):
    command_process_object = command_entities_process_objects.get(command.entity)
    if not command_process_object:
        command.failed_by_invalid_entity()
        return

    conditions = Q(pk=command.data.get('id'))
    if command.data.get('parent_entity_local_id') is not None:
        conditions |= Q(local_id=command.data.get('parent_entity_local_id'))
    entity = command_process_object.model.objects.filter(conditions).first()

    if not entity:
        command.failed_by_missed_entity()
        return

    serializer_context = {
        'data': command.data,
        'partial': True,
        'context': {
            'request': Request(User.all_objects.filter(pk=command.user).get(), []),
            'project_pk': command.project_id
        },
    }

    if command_process_object.handler:
        handler_context = {
            'user': serializer_context['context']['request'].user,
            'project_pk': serializer_context['context']['project_pk']
        }
        if command_process_object.use_command_in_handler:
            handler_context['command'] = command
    else:
        handler_context = serializer_context

    serializer = command_process_object.serializer(**serializer_context)
    validate(serializer, command)
    if command.is_failed:
        return

    perform_update(entity, command_process_object, serializer, serializer_context, handler_context, command)


def delete_entity(command: CommandModel):
    command_process_object = command_entities_process_objects.get(command.entity)
    if not command_process_object:
        command.failed_by_invalid_entity()
        return

    conditions = Q(pk=command.data.get('id'))
    if command.data.get('parent_entity_local_id') is not None:
        conditions |= Q(local_id=command.data.get('parent_entity_local_id'))
    entity = command_process_object.model.objects.filter(conditions).first()

    if not entity:
        command.failed_by_missed_entity()
        return

    perform_action(lambda: entity.delete(), command)


def restore_entity(command: CommandModel):
    command_process_object = command_entities_process_objects.get(command.entity)
    if not command_process_object:
        command.failed_by_invalid_entity()
        return

    if not is_safedelete_cls(command_process_object.model):
        command.failed_by_non_restorable_entity()
        return

    conditions = Q(pk=command.data.get('id'))
    if command.data.get('parent_entity_local_id') is not None:
        conditions |= Q(local_id=command.data.get('parent_entity_local_id'))
    entity = command_process_object.model.deleted_objects.filter(conditions).first()

    if not entity:
        command.failed_by_missed_entity()
        return

    perform_action(lambda: entity.undelete(), command)


def capture_fail(e, fail_reason, command) -> None:
    with sentry_sdk.push_scope() as scope:
        error_uuid = str(uuid.uuid4())
        scope.set_tag('error_uuid', error_uuid)
        command.mark_as_failed(error_uuid=error_uuid, fail_reason=fail_reason)
        capture_exception(e)
