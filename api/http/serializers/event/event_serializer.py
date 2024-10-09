import pendulum
from rest_framework.fields import ChoiceField, DateTimeField, IntegerField, CharField
from rest_framework_mongoengine.fields import DictField, ObjectIdField
from rest_framework_mongoengine.serializers import DocumentSerializer

from api.enums.entities import Entities
from api.models import Event


class EventSerializer(DocumentSerializer):
    class Meta:
        model = Event
        fields = ('id', 'data', 'type', 'entity', 'local_id', 'project_id', 'created_at', 'updated_at',)

    id = ObjectIdField(read_only=True)
    data = DictField(required=False, allow_null=True)
    type = ChoiceField(choices=Event.Types.choices(), required=True)
    entity = ChoiceField(choices=Entities.choices(), required=True)
    local_id = CharField(required=False, allow_null=True, default=None)
    project_id = IntegerField(allow_null=True)
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)

    def create(self, validated_data):
        validated_data = {**validated_data, **{
            'user': self.context['request'].user.pk,
            'created_at': pendulum.now(),
            'updated_at': pendulum.now(),
        }}

        return super().create(validated_data)
