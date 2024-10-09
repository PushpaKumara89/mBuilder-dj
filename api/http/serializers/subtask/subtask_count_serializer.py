from rest_framework import fields

from api.http.serializers import BaseModelSerializer
from api.models import Subtask


class SubtaskCountSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = (
            'total', 'closed', 'in_progress', 'removed', 'contested', 'under_inspection',
            'inspection_rejected', 'requesting_approval', 'declined', 'requested_approval_rejected'
        )

    total = fields.IntegerField(read_only=True)
    closed = fields.IntegerField(read_only=True)
    in_progress = fields.IntegerField(read_only=True)
    removed = fields.IntegerField(read_only=True)
    contested = fields.IntegerField(read_only=True)
    under_inspection = fields.IntegerField(read_only=True)
    inspection_rejected = fields.IntegerField(read_only=True)
    requested_approval_rejected = fields.IntegerField(read_only=True)
    requesting_approval = fields.IntegerField(read_only=True)
    declined = fields.IntegerField(read_only=True)
