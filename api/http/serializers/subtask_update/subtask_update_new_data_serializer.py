from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers import BaseModelSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_change_serializer import \
    FloorPlanAreaPinChangeSerializer
from api.models import Subtask, Task, Media, Company, PackageMatrixCompany, QualityIssue


class SubtaskUpdateNewDataSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = ('status', 'company', 'description', 'task', 'files', 'estimation',
                  'due_date', 'location_description', 'local_id', 'quality_issue',
                  'floor_plan_area_pin',)

    description = fields.CharField(required=False)
    location_description = fields.CharField(required=False, allow_null=True, allow_blank=True)
    status = fields.ChoiceField(required=True, choices=Subtask.Status.choices)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)
    files = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), many=True, required=False)
    quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=False, allow_null=True)
    estimation = fields.IntegerField(required=False, allow_null=True)
    due_date = fields.DateTimeField(required=False)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True)
    local_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    floor_plan_area_pin = FloorPlanAreaPinChangeSerializer(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields') if 'exclude_fields' in kwargs else []
        keys = list(self.fields.keys())

        for field in keys:
            if field in exclude_fields:
                self.fields.pop(field)

        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError(_('Got unknown fields: {}'.format(unknown_keys)))

        if attrs.get('company'):
            def activity_has_restrictions_by_company():
                return PackageMatrixCompany.objects.filter(
                    package_matrix__project_id=self.context['project_pk'],
                    package_matrix__package_activity_id=package_activity
                ).exists()

            def does_company_from_white_list():
                return PackageMatrixCompany.objects.filter(
                    package_matrix__project_id=self.context['project_pk'],
                    package_matrix__package_activity_id=package_activity,
                    company=attrs['company']
                ).exists()

            package_activity = attrs['task'].package_activity_id \
                if 'task' in attrs \
                else self.instance.task.package_activity_id

            if activity_has_restrictions_by_company() and not does_company_from_white_list():
                raise ValidationError({
                    'company': _('You should select only companies that assigned on package activities.')
                })

        return attrs
