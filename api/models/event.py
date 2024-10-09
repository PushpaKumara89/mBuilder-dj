from mongoengine import *

from api.enums import ChoiceEnum
from api.enums.entities import Entities


class Event(Document):
    class Types(ChoiceEnum):
        ENTITY_CREATED = 'entity_created'
        ENTITY_UPDATED = 'entity_updated'
        ENTITY_DELETED = 'entity_deleted'
        ENTITY_RESTORED = 'entity_restored'

    data = DictField(required=True)
    type = StringField(choices=Types.choices(), required=True)
    entity = StringField(choices=Entities.choices(), required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    local_id = StringField(required=False, null=True)
    project_id = IntField(null=True)
    user = IntField(required=False, null=True)

    meta = {
        'indexes': [
            'created_at',
        ]
    }

    @property
    def is_entity_created(self):
        return self.type == self.Types.ENTITY_CREATED.value

    @property
    def is_entity_updated(self):
        return self.type == self.Types.ENTITY_UPDATED.value

    @property
    def is_entity_deleted(self):
        return self.type == self.Types.ENTITY_DELETED.value

    @property
    def is_entity_restored(self):
        return self.type == self.Types.ENTITY_RESTORED.value
