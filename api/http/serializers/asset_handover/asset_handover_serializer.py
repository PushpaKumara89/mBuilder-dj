from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_read_serializer import \
    AssetHandoverStatisticsReadSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandover, PackageActivity, LocationMatrix, Project


class AssetHandoverSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandover
        fields = ('id', 'package_activity', 'location_matrix', 'project', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                fields=['package_activity', 'location_matrix'], queryset=AssetHandover.objects.all()
            )
        ]
        expandable_fields = {
            'expanded_asset_handover_information': ('api.http.serializers.AssetHandoverInformationSerializer', {'source': 'assethandoverinformation'}),
            'expanded_asset_handover_documents': ('api.http.serializers.AssetHandoverDocumentSerializer', {'source': 'assethandoverdocument_set', 'many': True}),
            'expanded_location_matrix': ('api.http.serializers.LocationMatrixSerializer', {'source': 'location_matrix'}),
            'expanded_package_activity': ('api.http.serializers.PackageActivitySerializer', {'source': 'package_activity'})
        }

    package_activity = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageActivity.objects.all())
    location_matrix = serializers.PrimaryKeyRelatedField(required=True, queryset=LocationMatrix.objects.all())
    project = serializers.PrimaryKeyRelatedField(required=True, queryset=Project.objects.all())
