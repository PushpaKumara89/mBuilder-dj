from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Project, User


class ProjectKeyContactsSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = ('key_contacts',)

    key_contacts = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all(), many=True)
