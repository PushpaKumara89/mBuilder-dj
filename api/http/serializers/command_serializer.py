import pendulum
from rest_framework.fields import ChoiceField, DateTimeField, IntegerField
from rest_framework_mongoengine.fields import DictField, ObjectIdField
from rest_framework_mongoengine.serializers import DocumentSerializer

from api.enums.entities import Entities
from api.models import Command


class CommandSerializer(DocumentSerializer):
    class Meta:
        model = Command
        fields = ('id', 'data', 'type', 'status', 'entity', 'project_id', 'created_at', 'updated_at',
                  'related_entities_local_ids', 'user',)

    id = ObjectIdField(read_only=True)
    data = DictField(required=False, allow_null=True)
    type = ChoiceField(choices=Command.Types.choices(), required=True)
    user = IntegerField(allow_null=True, required=False, default=None)
    status = ChoiceField(choices=Command.Statuses.choices(), required=False, default=Command.Statuses.PENDING.value)
    entity = ChoiceField(choices=Entities.choices(), required=True)
    project_id = IntegerField(allow_null=True)
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)
    related_entities_local_ids = DictField(required=False)

    def create(self, validated_data):
        validated_data = {**validated_data, **{
            'user': self.context['request'].user.pk,
            'created_at': pendulum.now(),
            'updated_at': pendulum.now(),
        }}

        return super().create(validated_data)
