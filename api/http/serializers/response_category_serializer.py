from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import UniqueTogetherValidator
from api.models import ResponseCategory, Project


class ResponseCategorySerializer(BaseModelSerializer):
    class Meta:
        model = ResponseCategory
        fields = ('id', 'name', 'description', 'project', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_project': ('api.http.serializers.ProjectSerializer', {'source': 'project'})
        }
        validators = [
            UniqueTogetherValidator(
                fields=['name', 'project'], queryset=ResponseCategory.objects.all(), lookup='iexact'
            )
        ]

    name = fields.CharField(max_length=255, required=True)
    description = fields.CharField(required=False, allow_null=True, allow_blank=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
