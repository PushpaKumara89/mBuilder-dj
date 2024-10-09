from rest_framework import fields


from api.http.serializers import BaseModelSerializer
from api.models import QualityIssue


class QualityIssueCountSerializer(BaseModelSerializer):
    class Meta:
        model = QualityIssue
        fields = (
            'total', 'removed', 'contested', 'in_progress', 'under_inspection', 'declined', 'under_review',
            'inspection_rejected', 'requesting_approval', 'requested_approval_rejected', 'closed'
        )

    total = fields.IntegerField(read_only=True)
    removed = fields.IntegerField(read_only=True)
    contested = fields.IntegerField(read_only=True)
    in_progress = fields.IntegerField(read_only=True)
    under_inspection = fields.IntegerField(read_only=True)
    under_review = fields.IntegerField(read_only=True)
    inspection_rejected = fields.IntegerField(read_only=True)
    requesting_approval = fields.IntegerField(read_only=True)
    requested_approval_rejected = fields.IntegerField(read_only=True)
    closed = fields.IntegerField(read_only=True)
    declined = fields.IntegerField(read_only=True)
