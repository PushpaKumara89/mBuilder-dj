from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageHandoverStatistics


class PackageHandoverStatisticsReadSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverStatistics
        fields = ('in_progress_count', 'accepted_count', 'removed_count',
                  'contested_count', 'requesting_approval_count',
                  'requested_approval_rejected_count')

    accepted_count = serializers.IntegerField(read_only=True)
    in_progress_count = serializers.IntegerField(read_only=True)
    contested_count = serializers.IntegerField(read_only=True)
    removed_count = serializers.IntegerField(read_only=True)
    requested_approval_rejected_count = serializers.IntegerField(read_only=True)
    requesting_approval_count = serializers.IntegerField(read_only=True)
