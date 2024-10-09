from api.http.serializers import LastEntityListSerializer
from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_read_serializer import \
    AssetHandoverStatisticsReadSerializer


class LastAssetHandoverStatisticsSerializer(AssetHandoverStatisticsReadSerializer):
    class Meta(AssetHandoverStatisticsReadSerializer.Meta):
        list_serializer_class = LastEntityListSerializer
