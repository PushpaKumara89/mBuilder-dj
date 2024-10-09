from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models.project_user import ProjectUser


class ProjectUserSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectUser
        fields = ('is_notifications_enabled', 'project', 'user')
        expandable_fields = {
            'expanded_project': ('api.http.serializers.ProjectSerializer', {'source': 'project'}),
            'expanded_user': ('api.http.serializers.UserSerializer', {'source': 'user'})
        }

    is_notifications_enabled = serializers.BooleanField(required=False)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
