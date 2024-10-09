from rest_framework import fields
from rest_framework import serializers
from api.http.serializers import PackageActivitySerializer, TaskSerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.http.serializers.task_update.task_update_serializer import TaskUpdateSerializer
from api.models import Task


class TaskRestrictedReadSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = (
            'id', 'status', 'package_activity', 'package_activity_task',
            'location_matrix', 'date_of_approval', 'local_id'
        )
        expandable_fields = {
            'expanded_subtasks': ('api.http.serializers.SubtaskSerializer', {'many': True, 'source': 'subtask_set'}),
            'expanded_attachments': (serializers.SerializerMethodField, {'method_name': 'attachments'}),
            'expanded_comment': (serializers.SerializerMethodField, {'method_name': 'comment'}),
            'expanded_location_matrix': (LocationMatrixSerializer, {'source': 'location_matrix'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'package'}),
            'expanded_last_attachments': (serializers.SerializerMethodField, {'method_name': 'get_last_attachments'}),
            'expanded_updates': (TaskUpdateSerializer, {'many': True, 'source': 'taskupdate_set'}),
        }

    package_activity = PackageActivitySerializer(omit=['package_activity_tasks'], read_only=True)
    package_activity_task = PackageActivityTaskSerializer(read_only=True)
    location_matrix = LocationMatrixSerializer(read_only=True)
    status = fields.CharField(read_only=True)
    date_of_approval = fields.DateTimeField(read_only=True)
    local_id = serializers.CharField(read_only=True)
