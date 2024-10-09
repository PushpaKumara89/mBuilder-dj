from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageMatrix, PackageActivity, Package


class PackageMatrixCreateSerializer(BaseModelSerializer):
    class Meta:
        model = PackageMatrix
        fields = ('package', 'package_activity',)

    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    package_activity = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageActivity.objects.all(), many=True)
