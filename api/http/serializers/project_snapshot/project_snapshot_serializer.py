import pendulum

from rest_framework.fields import DateTimeField, IntegerField
from rest_framework_mongoengine.fields import DictField, ObjectIdField
from rest_framework_mongoengine.serializers import DocumentSerializer

from api.models.project_snapshot import ProjectSnapshot


class ProjectSnapshotSerializer(DocumentSerializer):
    class Meta:
        model = ProjectSnapshot
        fields = ('id', 'data', 'project_id', 'created_at', 'updated_at', 'generation_started_at',)

    id = ObjectIdField(read_only=True)
    data = DictField(required=False, allow_null=True)
    project_id = IntegerField(allow_null=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    generation_started_at = DateTimeField(required=True)

    def create(self, validated_data):
        creation_data = {
            **validated_data,
            'created_at': pendulum.now().to_datetime_string(),
            'updated_at': pendulum.now().to_datetime_string(),
        }

        return super().create(creation_data)
