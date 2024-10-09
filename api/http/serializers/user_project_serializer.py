from rest_framework import fields
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Project


class UserProjectSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name',)

    id = fields.ReadOnlyField()
    name = fields.ReadOnlyField()
