from rest_framework import fields, serializers

from api.http.serializers import ProjectSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetRegister, Project


class AssetRegisterSerializer(BaseModelSerializer):
    class Meta:
        model = AssetRegister
        fields = ('id', 'data', 'project', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_project': (ProjectSerializer, {'source': 'project'})
        }

    data = fields.JSONField(required=True)
    project = serializers.PrimaryKeyRelatedField(required=True, queryset=Project.objects.all())
