from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_editable_data_serializer import \
    AssetHandoverDocumentEditableDataSerializer
from api.models import AssetHandover, AssetHandoverDocument


class AssetHandoverDocumentSerializer(AssetHandoverDocumentEditableDataSerializer):
    class Meta(AssetHandoverDocumentEditableDataSerializer.Meta):
        fields = AssetHandoverDocumentEditableDataSerializer.Meta.fields + (
            'asset_handover', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                fields=['asset_handover', 'document_type'], queryset=AssetHandoverDocument.objects.all()
            )
        ]
        expandable_fields = {
            'expanded_document_type': ('api.http.serializers.AssetHandoverDocumentTypeSerializer', {'source': 'document_type'}),
            'expanded_asset_handover': ('api.http.serializers.AssetHandoverSerializer', {'source': 'asset_handover'}),
            'expanded_asset_handover_document_media': ('api.http.serializers.asset_handover.AssetHandoverDocumentMediaRestrictedViewSerializer', {'source': 'assethandoverdocumentmedia_set', 'many': True}),
            'expanded_asset_handover_statistics': ('api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_aggregation_serializer.AssetHandoverStatisticsAggregationSerializer', {'source': 'assethandoverstatistics_set', 'many': True}),
        }

    asset_handover = serializers.PrimaryKeyRelatedField(required=True, queryset=AssetHandover.objects.all())
