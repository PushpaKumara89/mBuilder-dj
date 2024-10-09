from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import TaskUpdate, Task, User, Media
from api.http.serializers.user.user_serializer import UserSerializer
from api.http.serializers import MediaSerializer
from .. import RecipientSerializer


class TaskUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = (
            'id', 'task', 'user', 'comment', 'files', 'old_data', 'new_data', 'created_at',
            'updated_at', 'recipients', 'is_conflict', 'local_id',
        )
        expandable_fields = {
            'expanded_recipients': (RecipientSerializer, {'many': True, 'source': 'recipients'}),
            'expanded_task': ('api.http.serializers.TaskSerializer', {'source': 'task'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'}),
        }

    id = fields.ReadOnlyField()
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    comment = fields.CharField(required=False, allow_null=True)
    files = serializers.PrimaryKeyRelatedField(required=False, queryset=Media.objects.all(), many=True, allow_null=False, allow_empty=True)
    old_data = fields.JSONField(required=True)
    new_data = fields.JSONField(required=False)
    recipients = RecipientSerializer(required=False, many=True)
    is_conflict = fields.BooleanField(required=False, default=False)
    local_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
