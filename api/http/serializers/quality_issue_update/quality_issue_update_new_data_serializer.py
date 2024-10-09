from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_change_serializer import \
    FloorPlanAreaPinChangeSerializer
from api.models import QualityIssue, Media, LocationMatrix, ResponseCategory


class QualityIssueUpdateNewDataSerializer(BaseModelSerializer):
    class Meta:
        model = QualityIssue
        fields = ('status', 'description', 'attachments', 'location_matrix', 'due_date', 'local_id',
                  'response_category', 'floor_plan_area_pin')

    status = fields.ChoiceField(choices=QualityIssue.Status.choices, required=False)
    location_matrix = serializers.PrimaryKeyRelatedField(queryset=LocationMatrix.objects.all(), required=False)
    description = fields.CharField(required=False)
    attachments = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, many=True)
    due_date = fields.DateTimeField(required=False)
    local_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    response_category = serializers.PrimaryKeyRelatedField(queryset=ResponseCategory.objects.all(), allow_null=True, required=False)
    floor_plan_area_pin = FloorPlanAreaPinChangeSerializer(required=False, partial=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        self.status_sync = kwargs.pop('status_sync') if 'status_sync' in kwargs else False

        exclude_fields = kwargs.pop('exclude_fields') if 'exclude_fields' in kwargs else []
        keys = list(self.fields.keys())

        for field in keys:
            if field in exclude_fields:
                self.fields.pop(field)

        super().__init__(*args, **kwargs)

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            initial_data_keys = set(self.initial_data.keys())
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError(_('Got unknown fields: {}'.format(unknown_keys)))

            if not self.status_sync and self.instance.status == QualityIssue.Status.CLOSED and 'status' in initial_data_keys:
                raise ValidationError({'status': _('You cannot change status for closed quality issue.')})

        return data
