from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverStatistics


class AssetHandoverProjectStatisticsReadSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverStatistics
        fields = ('accepted_count', 'contested_count', 'in_progress_count',
                  'removed_count', 'requested_approval_rejected_count',
                  'requesting_approval_count',
                  'total_information_count', 'filled_information_count',
                  'uploaded_files_count', 'required_files_count')

    accepted_count = serializers.IntegerField(read_only=True)
    contested_count = serializers.IntegerField(read_only=True)
    in_progress_count = serializers.IntegerField(read_only=True)
    removed_count = serializers.IntegerField(read_only=True)
    requested_approval_rejected_count = serializers.IntegerField(read_only=True)
    requesting_approval_count = serializers.IntegerField(read_only=True)

    total_information_count = serializers.IntegerField(read_only=True)
    filled_information_count = serializers.IntegerField(read_only=True)

    required_files_count = serializers.IntegerField(read_only=True)
    uploaded_files_count = serializers.IntegerField(read_only=True)
