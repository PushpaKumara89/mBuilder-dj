from api.http.serializers.last_entity_list_serializer import LastEntityListSerializer
from api.http.serializers.quality_issue_update.quality_issue_update_serializer import QualityIssueUpdateSerializer


class QualityIssueLastUpdateSerializer(QualityIssueUpdateSerializer):
    class Meta(QualityIssueUpdateSerializer.Meta):
        list_serializer_class = LastEntityListSerializer
