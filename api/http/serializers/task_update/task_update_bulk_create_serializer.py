from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.task_update.task_update_bulk_create_item_serializer import TaskUpdateBulkCreateItemSerializer
from api.models import TaskUpdate, User, Media
from .. import RecipientSerializer


class TaskUpdateBulkCreateSerializer(BaseModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = (
            'id', 'user', 'new_data', 'task_updates', 'comment', 'files', 'recipients'
        )

    task_updates = TaskUpdateBulkCreateItemSerializer(many=True, required=True)

    new_data = fields.JSONField(required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    comment = fields.CharField(required=False, allow_null=True)
    files = serializers.PrimaryKeyRelatedField(required=False, queryset=Media.objects.all(), many=True, allow_null=False, allow_empty=True)
    recipients = RecipientSerializer(required=False, many=True)
