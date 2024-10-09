from api.http.serializers.package_handover.package_handover_statistics.package_handover_statistics_read_serializer import \
    PackageHandoverStatisticsReadSerializer
from api.http.serializers.statistics_aggregation_list_serializer import StatisticsAggregationListSerializer


class PackageHandoverStatisticsAggregationListSerializer(StatisticsAggregationListSerializer):
    aggregation_fields_serializer_class = PackageHandoverStatisticsReadSerializer

    def _skip_field(self, field_name: str) -> bool:
        return False
