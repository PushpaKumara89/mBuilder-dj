from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import TaskUpdate, Task


class TaskUpdateBulkCreateItemSerializer(BaseModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = (
            'task', 'old_data', 'created_at', 'updated_at',
        )

    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    old_data = fields.JSONField(required=True)
