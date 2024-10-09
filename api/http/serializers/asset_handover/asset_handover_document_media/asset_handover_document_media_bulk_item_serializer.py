from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverDocumentMedia, PackageActivity, LocationMatrix, Package


class AssetHandoverDocumentMediaBulkItemSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('package_activity', 'location_matrix', 'package')

    package_activity = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageActivity.objects.all())
    location_matrix = serializers.PrimaryKeyRelatedField(required=True, queryset=LocationMatrix.objects.all())
    package = serializers.PrimaryKeyRelatedField(required=True, queryset=Package.objects.all())
