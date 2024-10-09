from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverStatistics, Project, Company


class AssetHandoverStatisticsSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverStatistics
        fields = ('project', 'required_files_count', 'uploaded_files_count', 'object_id', 'content_type', 'group',
                  'statistics_by_statuses', 'total_information_count', 'filled_information_count', 'company')

    content_type = serializers.PrimaryKeyRelatedField(required=True, queryset=ContentType.objects.all())
    object_id = serializers.IntegerField(required=True)
    required_files_count = serializers.IntegerField(required=False)
    uploaded_files_count = serializers.IntegerField(required=False)
    total_information_count = serializers.IntegerField(required=False)
    filled_information_count = serializers.IntegerField(required=False)
    statistics_by_statuses = serializers.JSONField(required=False)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)
