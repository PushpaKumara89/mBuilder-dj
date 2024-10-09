from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_read_serializer import \
    AssetHandoverStatisticsReadSerializer
from api.http.serializers.statistics_aggregation_list_serializer import StatisticsAggregationListSerializer
from api.models import AssetHandoverDocumentMedia


class AssetHandoverStatisticsAggregationListSerializer(StatisticsAggregationListSerializer):
    aggregation_fields_serializer_class = AssetHandoverStatisticsReadSerializer

    def _skip_field(self, field_name: str) -> bool:
        if self.child.context['request'].user.is_client:
            return field_name not in (
                f'{AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL}_count',
                f'{AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED}_count',
                f'{AssetHandoverDocumentMedia.Status.ACCEPTED}_count',
            )
        elif self.child.context['request'].user.is_consultant:
            return field_name != f'{AssetHandoverDocumentMedia.Status.ACCEPTED}_count'

        return False
