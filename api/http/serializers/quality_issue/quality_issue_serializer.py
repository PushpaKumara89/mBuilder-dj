from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import ReadOnlyField

from api.http.serializers import MediaSerializer, RecipientSerializer, SubtaskSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_create_serializer import \
    FloorPlanAreaPinCreateSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_quality_issue_pin_serializer import \
    FloorPlanAreaQualityIssuePinSerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.quality_issue_update.quality_issue_last_update_serializer import QualityIssueLastUpdateSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.models import QualityIssue, LocationMatrix, Media, User, Subtask, ResponseCategory


class QualityIssueSerializer(BaseModelSerializer):
    class Meta:
        model = QualityIssue
        fields = ('id', 'location_matrix', 'user', 'description', 'status', 'attachments',
                  'recipients', 'created_at', 'updated_at', 'due_date', 'last_confirmed_update',
                  'old_quality_issue', 'local_id', 'response_category', 'floor_plan_area_pin')
        expandable_fields = {
            'expanded_location_matrix': (LocationMatrixSerializer, {'source': 'location_matrix'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_attachments': (MediaSerializer, {'many': True, 'source': 'attachments'}),
            'expanded_subtasks': (SubtaskSerializer, {'source': 'subtask_set', 'many': True}),
            'expanded_in_work_subtasks_count': (serializers.SerializerMethodField, {'method_name': 'in_work_subtasks_count'}),
            'expanded_last_confirmed_update': ('api.http.serializers.QualityIssueUpdateSerializer', {'source': 'last_confirmed_update'}),
            'expanded_last_status_change_update': (serializers.SerializerMethodField, {'method_name': 'last_status_change_update'}),
            'expanded_old_quality_issue': ('api.http.serializers.QualityIssueSerializer', {'source': 'old_quality_issue'}),
            'expanded_last_recipients': ('api.http.serializers.QualityIssueLastRecipientSerializer',
                                         {'many': True, 'source': 'qualityissueupdate_set'}),
            'expanded_last_update': (QualityIssueLastUpdateSerializer, {'many': True, 'source': 'qualityissueupdate_set'}),
            'expanded_updates': ('api.http.serializers.QualityIssueUpdateSerializer', {'many': True, 'source': 'qualityissueupdate_set'}),
            'expanded_response_category': ('api.http.serializers.ResponseCategorySerializer', {'source': 'response_category'}),
            'expanded_floor_plan_area_pin': (FloorPlanAreaQualityIssuePinSerializer, {'source': 'floor_plan_area_pin'})
        }

    id = ReadOnlyField()
    location_matrix = serializers.PrimaryKeyRelatedField(queryset=LocationMatrix.objects.all(), required=True)
    description = serializers.CharField(required=True)
    status = serializers.ReadOnlyField()
    attachments = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    recipients = RecipientSerializer(required=False, many=True)
    due_date = serializers.DateTimeField(required=True)
    last_confirmed_update = serializers.PrimaryKeyRelatedField(read_only=True)
    old_quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=False,
                                                           allow_null=True)
    local_id = serializers.CharField(required=False, max_length=255, allow_null=True, allow_blank=True)
    response_category = serializers.PrimaryKeyRelatedField(queryset=ResponseCategory.objects.all(), allow_null=True, required=False)
    floor_plan_area_pin = FloorPlanAreaPinCreateSerializer(required=False, write_only=True, allow_null=True)

    def validate(self, attrs):
        response_category = attrs.get('response_category')
        if response_category and response_category.project.pk != attrs['location_matrix'].project.pk:
            raise ValidationError({'response_category': _('You should select response category from'
                                                          ' same project as quality issue.')})

        return attrs

    def validate_location_matrix(self, location_matrix: LocationMatrix):
        if 'project_pk' in self.context and location_matrix.project_id != self.context['project_pk']:
            raise ValidationError(_('Location matrix should be from the current project.'))

        return location_matrix

    def in_work_subtasks_count(self, obj: QualityIssue):
        if hasattr(obj, 'opened_subtasks'):
            return len(obj.opened_subtasks)

        return obj.subtask_set.filter(status__in=[
            Subtask.Status.CONTESTED, Subtask.Status.INSPECTION_REJECTED,
            Subtask.Status.IN_PROGRESS, Subtask.Status.UNDER_INSPECTION
        ]).count()

    def last_status_change_update(self, obj: QualityIssue):
        from api.http.serializers.quality_issue_update.quality_issue_update_serializer import QualityIssueUpdateSerializer

        update = self._get_last_status_change_update(obj)

        if update:
            return QualityIssueUpdateSerializer(update, context=self.context).data

        return None

    def _get_last_status_change_update(self, obj: QualityIssue):
        if hasattr(obj, 'last_updates_with_changed_status'):
            return obj.last_updates_with_changed_status[0] if obj.last_updates_with_changed_status else None

        return obj.qualityissueupdate_set.all().get_with_changed_status_in_desc_order().first()
