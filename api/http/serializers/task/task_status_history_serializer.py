from rest_framework import fields, serializers

from api.http.serializers import BaseModelSerializer, UserSerializer
from api.http.serializers.task_update.task_update_new_data_serializer import TaskUpdateNewDataSerializer
from api.models import TaskUpdate, Task


class TaskStatusHistorySerializer(BaseModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = ('status', 'user', 'comment', 'created_at')

    comment = fields.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    def get_status(self, obj: TaskUpdate):
        new_data_serializer = TaskUpdateNewDataSerializer(obj.new_data)

        if status := new_data_serializer.data.get('status'):
            return dict(Task.Statuses.choices)[status]
        return None
