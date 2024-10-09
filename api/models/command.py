from mongoengine import *

from api.enums import ChoiceEnum
from api.enums.entities import Entities


class Command(Document):
    class Types(ChoiceEnum):
        CREATE_ENTITY = 'create_entity'
        UPDATE_ENTITY = 'update_entity'
        DELETE_ENTITY = 'delete_entity'
        RESTORE_ENTITY = 'restore_entity'

    class Statuses(ChoiceEnum):
        CONFLICTED = 'conflicted'
        PROCESSED = 'processed'
        PENDING = 'pending'
        FAILED = 'failed'

    class FailReason(ChoiceEnum):
        VALIDATION_ERROR = 'validation_error'
        INTERNAL_ERROR = 'internal_error'
        NON_RESTORABLE_ENTITY = 'non_restorable_entity'
        MISSED_ENTITY = 'missed_entity'
        MISSED_PARENT_ENTITY = 'missed_parent_entity'
        INVALID_ENTITY = 'invalid_entity'

    data = DictField(required=True)
    type = StringField(choices=Types.choices(), required=True)
    status = StringField(choices=Statuses.choices(), required=True)
    entity = StringField(choices=Entities.choices(), required=True)
    fail_reason = StringField(required=False, null=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    project_id = IntField(null=True)
    user = IntField(required=False, null=True)
    related_entities_local_ids = DictField(required=False, null=True)
    error_uuid = StringField(required=False, null=True)

    meta = {
        'collection': 'command_model',
        'indexes': [
            ('status', 'created_at',),
            {'fields': ['data.local_id'], 'unique': True, 'sparse': True},
        ]
    }

    @property
    def is_entity_create(self):
        return self.type == self.Types.CREATE_ENTITY.value

    @property
    def is_entity_update(self):
        return self.type == self.Types.UPDATE_ENTITY.value

    @property
    def is_entity_delete(self):
        return self.type == self.Types.DELETE_ENTITY.value

    @property
    def is_entity_restore(self):
        return self.type == self.Types.RESTORE_ENTITY.value

    @property
    def is_conflicted(self):
        return self.status == self.Statuses.CONFLICTED.value

    @property
    def is_pending(self):
        return self.status == self.Statuses.PENDING.value

    @property
    def is_failed(self):
        return self.status == self.Statuses.FAILED.value

    @property
    def is_processed(self):
        return self.status == self.Statuses.PROCESSED.value

    def mark_as_failed(self, fail_reason: FailReason = None, error_uuid: str = None):
        self.update(fail_reason=fail_reason.value, status=self.Statuses.FAILED.value, error_uuid=error_uuid)
        self.reload()

    def mark_as_processed(self):
        self.update(status=self.Statuses.PROCESSED.value)
        self.reload()

    def mark_as_conflicted(self):
        self.update(status=self.Statuses.CONFLICTED.value)
        self.reload()

    def failed_by_non_restorable_entity(self):
        self.update(fail_reason=self.FailReason.NON_RESTORABLE_ENTITY.value, status=self.Statuses.FAILED.value)
        self.reload()

    def failed_by_missed_entity(self):
        self.update(fail_reason=self.FailReason.MISSED_ENTITY.value, status=self.Statuses.FAILED.value)
        self.reload()

    def failed_by_missed_parent_entity(self):
        self.update(fail_reason=self.FailReason.MISSED_PARENT_ENTITY.value, status=self.Statuses.FAILED.value)
        self.reload()

    def failed_by_invalid_entity(self):
        self.update(fail_reason=self.FailReason.INVALID_ENTITY.value, status=self.Statuses.FAILED.value)
        self.reload()
