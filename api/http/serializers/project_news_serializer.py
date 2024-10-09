from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models.project import Project
from api.models.project_news import ProjectNews


class ProjectNewsSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectNews
        fields = ('id', 'title', 'date', 'text', 'created_at', 'updated_at', 'project_id',)

    id = fields.ReadOnlyField()
    title = fields.CharField(required=True, max_length=255)
    text = fields.CharField(required=True, max_length=None)
    date = fields.DateField(required=False)
    project_id = serializers.PrimaryKeyRelatedField(required=False, write_only=True, queryset=Project.objects.all())
