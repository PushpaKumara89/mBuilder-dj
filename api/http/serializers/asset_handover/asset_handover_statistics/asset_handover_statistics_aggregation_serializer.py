from api.http.serializers import BaseModelSerializer
from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_aggregation_list_serializer import \
    AssetHandoverStatisticsAggregationListSerializer


class AssetHandoverStatisticsAggregationSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer):
        list_serializer_class = AssetHandoverStatisticsAggregationListSerializer
