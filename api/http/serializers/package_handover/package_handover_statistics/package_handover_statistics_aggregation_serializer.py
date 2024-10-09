from api.http.serializers import BaseModelSerializer
from api.http.serializers.package_handover.package_handover_statistics.package_handover_statistics_aggregation_list_serializer import \
    PackageHandoverStatisticsAggregationListSerializer


class PackageHandoverStatisticsAggregationSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer):
        list_serializer_class = PackageHandoverStatisticsAggregationListSerializer
