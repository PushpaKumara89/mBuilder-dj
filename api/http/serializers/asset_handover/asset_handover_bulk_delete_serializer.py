from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandover, PackageActivity


class AssetHandoverBulkDeleteSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandover
        fields = ('id', 'package_activity')

    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=True)
