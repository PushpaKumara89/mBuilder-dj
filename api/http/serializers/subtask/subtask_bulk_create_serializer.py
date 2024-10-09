from rest_framework import fields, serializers

from api.http.serializers import UserSerializer, BaseModelSerializer, MediaSerializer, RecipientSerializer
from api.http.serializers.task import TaskSerializer
from api.models import Subtask, Task, User, Media, Company


class SubtaskBulkCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = (
            'id', 'description', 'is_closed', 'tasks', 'user', 'files',
            'recipients', 'estimation', 'due_date', 'status', 'company',
            'location_description',
        )
        expandable_fields = {
            'expanded_task': (TaskSerializer, {'source': 'task'}),
            'expanded_company': (TaskSerializer, {'source': 'company'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'})
        }

    description = fields.CharField(required=True)
    location_description = fields.CharField(required=False, allow_null=True, max_length=50, allow_blank=True)
    status = fields.ChoiceField(required=True, choices=Subtask.Status.choices)
    recipients = RecipientSerializer(required=False, many=True)
    tasks = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True, many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    files = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), many=True, required=False)
    estimation = fields.IntegerField(required=False, allow_null=True)
    due_date = fields.DateTimeField(required=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True, default=None)
