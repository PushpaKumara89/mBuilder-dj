from rest_framework import serializers

from api.http.serializers import RecipientSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import QualityIssue, Media, User, ResponseCategory


class QualityIssueBulkCreateSerializer(BaseModelSerializer):
    class Meta:
        model = QualityIssue
        fields = ('building', 'level', 'area', 'description', 'attachments',
                  'recipients', 'user', 'due_date', 'response_category',)

    building = serializers.CharField(required=True, max_length=255)
    level = serializers.CharField(required=True, max_length=255)
    area = serializers.ListField(required=False, child=serializers.CharField(max_length=255))
    description = serializers.CharField(required=True)
    attachments = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    recipients = RecipientSerializer(required=False, many=True)
    due_date = serializers.DateTimeField(required=True)
    response_category = serializers.PrimaryKeyRelatedField(queryset=ResponseCategory.objects.all(), allow_null=True, required=False)
