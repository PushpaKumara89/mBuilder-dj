from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverStatistics


class AssetHandoverProjectFilteredStatisticsReadSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverStatistics
        fields = ('total_information_count', 'filled_information_count',
                  'uploaded_files_count', 'required_files_count')

    total_information_count = serializers.IntegerField(read_only=True)
    filled_information_count = serializers.IntegerField(read_only=True)

    required_files_count = serializers.IntegerField(read_only=True)
    uploaded_files_count = serializers.IntegerField(read_only=True)
