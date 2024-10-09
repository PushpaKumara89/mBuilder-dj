from rest_framework import fields
from rest_framework import serializers
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Task, PackageActivity, PackageActivityTask, LocationMatrix, User


class TaskCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id', 'status', 'package_activity', 'package_activity_task', 'local_id',
            'location_matrix', 'user', 'date_of_approval', 'created_at', 'updated_at',
        )

    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all())
    package_activity_task = serializers.PrimaryKeyRelatedField(queryset=PackageActivityTask.objects.all())
    location_matrix = serializers.PrimaryKeyRelatedField(queryset=LocationMatrix.objects.all())
    status = fields.ChoiceField(choices=Task.Statuses.choices)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    date_of_approval = fields.DateTimeField(read_only=True)
    local_id = serializers.CharField(required=False, max_length=255, allow_null=True, allow_blank=True)
