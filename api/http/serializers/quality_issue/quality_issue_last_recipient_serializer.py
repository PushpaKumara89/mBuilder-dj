from rest_framework.serializers import ListSerializer
from api.http.serializers import RecipientSerializer
from api.models import QualityIssue


class QualityIssueLastRecipientListSerializer(ListSerializer):
    def update(self, instance, validated_data):
        pass

    def to_representation(self, data):
        recipients = []
        quality_issue: QualityIssue = getattr(data, 'instance', None)

        if hasattr(quality_issue, 'quality_issue_last_recipients'):
            if quality_issue.quality_issue_last_recipients:
                recipients = quality_issue.quality_issue_last_recipients[0].recipients.all()
        else:
            update = data.all().get_for_last_recipients().first()
            if update:
                recipients = update.recipients.all()

        return [self.child.to_representation(item) for item in recipients]


class QualityIssueLastRecipientSerializer(RecipientSerializer):
    class Meta(RecipientSerializer.Meta):
        list_serializer_class = QualityIssueLastRecipientListSerializer
