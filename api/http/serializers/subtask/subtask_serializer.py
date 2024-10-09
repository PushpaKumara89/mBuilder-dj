from typing import Optional

import pendulum
from django.db.models import CharField, Q
from django.db.models.expressions import RawSQL, Value
from django.db.models.functions import Concat

from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api.http.serializers import BaseModelSerializer, MediaSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_create_serializer import \
    FloorPlanAreaPinCreateSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_subtask_pin_serializer import \
    FloorPlanAreaSubtaskPinSerializer
from api.http.serializers.recipient_serializer import RecipientSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.task import TaskSerializer
from api.models import Subtask, Task, User, Media, QualityIssue, Company, PackageMatrixCompany, SubtaskUpdate


class SubtaskSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = (
            'id', 'description', 'is_closed', 'task', 'user', 'files', 'created_at',
            'updated_at', 'date_of_completion', 'recipients', 'estimation', 'due_date',
            'company', 'quality_issue', 'status', 'is_defect', 'last_confirmed_update',
            'response_due_date', 'location_description', 'local_id', 'floor_plan_area_pin',
            'files_count', 'closed_files_count'
        )
        expandable_fields = {
            'expanded_quality_issue': ('api.http.serializers.QualityIssueSerializer', {'source': 'quality_issue'}),
            'expanded_company': ('api.http.serializers.CompanySerializer', {'source': 'company'}),
            'expanded_task': (TaskSerializer, {'source': 'task'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'}),
            'expanded_closed_files': (serializers.SerializerMethodField, {'method_name': 'get_closed_files'}),
            'expanded_updates': ('api.http.serializers.SubtaskUpdateSerializer', {'many': True, 'source': 'subtaskupdate_set'}),
            'expanded_last_confirmed_update': ('api.http.serializers.SubtaskUpdateSerializer', {'source': 'last_confirmed_update'}),
            'expanded_last_status_change_update': (serializers.SerializerMethodField, {'method_name': 'last_status_change_update'}),
            'expanded_last_recipients': (serializers.SerializerMethodField, {'method_name': 'last_recipients'}),
            'expanded_last_update': ('api.http.serializers.SubtaskUpdateSerializer', {'source': 'last_update'}),
            'expanded_status_date': (serializers.SerializerMethodField, {'method_name': 'status_date'}),
            'expanded_location_matrix': (LocationMatrixSerializer, {'source': 'task.location_matrix'}),
            'expanded_floor_plan_area_pin': (FloorPlanAreaSubtaskPinSerializer, {'source': 'floor_plan_area_pin'}),
        }

    description = fields.CharField(required=True)
    location_description = fields.CharField(required=False, allow_null=True, max_length=50, allow_blank=True)
    is_closed = fields.BooleanField(read_only=True)
    status = fields.ChoiceField(required=True, choices=Subtask.Status.choices)
    recipients = RecipientSerializer(required=False, many=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    files = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), many=True, required=False)
    date_of_completion = fields.DateTimeField(read_only=True)
    estimation = fields.IntegerField(required=False, allow_null=True)
    due_date = fields.DateTimeField(required=True)
    response_due_date = fields.DateTimeField(required=False)
    created_at = fields.DateTimeField(required=False)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True,
                                                 default=None)
    quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=False,
                                                       allow_null=True, default=None, validators=[UniqueValidator(queryset=Subtask.objects.all())])
    is_defect = serializers.BooleanField(read_only=True)
    last_confirmed_update = serializers.PrimaryKeyRelatedField(read_only=True)
    local_id = serializers.CharField(required=False, max_length=255, allow_null=True, allow_blank=True)
    floor_plan_area_pin = FloorPlanAreaPinCreateSerializer(required=False, write_only=True, allow_null=True)
    files_count = serializers.IntegerField(read_only=True)
    closed_files_count = serializers.IntegerField(read_only=True)

    def last_recipients(self, subtask: Subtask) -> list:
        if hasattr(subtask, 'last_recipients_updates'):
            open_update = subtask.last_recipients_updates[0] if subtask.last_recipients_updates else None
        else:
            open_update = subtask.subtaskupdate_set.prefetch_related('files').annotate(
                transition=Concat(
                    RawSQL('old_data ->> %s', ('status',)),
                    Value('-'),
                    RawSQL('new_data ->> %s', ('status',)),
                    output_field=CharField()
                )
            ).filter(
                Q(transition=f'{Subtask.Status.IN_PROGRESS}-{Subtask.Status.IN_PROGRESS}') |
                Q(transition=f'{Subtask.Status.CONTESTED}-{Subtask.Status.IN_PROGRESS}') |
                Q(transition=f'-{Subtask.Status.IN_PROGRESS}')
            ).order_by('-created_at').first()

        if open_update:
            return RecipientSerializer(open_update.recipients, many=True).data

        return []

    def last_status_change_update(self, obj: Subtask) -> Optional[dict]:
        from api.http.serializers.subtask_update.subtask_update_serializer import SubtaskUpdateSerializer

        update = self._get_last_status_change_update(obj)

        if update:
            return SubtaskUpdateSerializer(update, context=self.context).data

        return None

    def status_date(self, obj: Subtask) -> Optional[str]:
        update = self._get_last_status_change_update(obj)

        if update:
            return pendulum.parse(str(update.created_at)).to_datetime_string()

        return None

    def _get_last_status_change_update(self, obj: Subtask) -> Optional[SubtaskUpdate]:
        if hasattr(obj, 'last_status_change_update'):
            return obj.last_status_change_update[0] if obj.last_status_change_update else None
        else:
            return obj.subtaskupdate_set.filter(
                ~Q(old_data__status=RawSQL('new_data -> %s', ('status',)))
            ).order_by('-created_at').first()

    def get_closed_files(self, obj: Subtask) -> list:
        if not obj.is_closed:
            return []

        if hasattr(obj, 'closed_files_updates'):
            subtask_updates = obj.closed_files_updates
        else:
            subtask_updates = obj.subtaskupdate_set.filter(
                new_data__status=Subtask.Status.CLOSED
            )
            
        files = []

        for subtask_update in subtask_updates:
            update_files = list(subtask_update.files.all())
            for file in update_files:
                files.append(file)

        return MediaSerializer(files, many=True, expand=[
            'expanded_project_snapshot_thumbnails.expanded_thumbnail',
            'expanded_thumbnails.expanded_thumbnail'
        ]).data

    def validate(self, attrs) -> dict:
        def does_company_from_white_list(company) -> bool:
            return PackageMatrixCompany.objects.filter(
                package_matrix__project=project_pk,
                package_matrix__package_activity=task.package_activity,
                company=company
            ).exists()

        def activity_has_restrictions_by_company() -> bool:
            return PackageMatrixCompany.objects.filter(
                package_matrix__project=project_pk, package_matrix__package_activity=task.package_activity
            ).exists()

        task = attrs['task'] if attrs.get('task') else self.instance.task
        project_pk = task.location_matrix.project_id

        if attrs.get('company'):
            if activity_has_restrictions_by_company() and not does_company_from_white_list(attrs['company']):
                raise ValidationError({
                    'company': _('You should select only companies that assigned on package activities.')
                })
        # Create new subtask without pointing required company.
        elif not self.instance and not attrs.get('company') and activity_has_restrictions_by_company():
            raise ValidationError({'company': self.error_messages['required']}, code='required')
        # Need to validate subtask company after changing task.
        elif self.instance and attrs.get('task'):
            company = attrs.get('company', self.instance.company)
            if not does_company_from_white_list(company):
                raise ValidationError({
                        'company': _('You should select only companies that assigned on package activities.')
                    })

        return attrs

    def validate_quality_issue(self, quality_issue: QualityIssue) -> QualityIssue:
        if quality_issue and 'project_pk' in self.context and quality_issue.location_matrix.project_id != self.context['project_pk']:
            raise ValidationError(_('The quality issue should be related to the same project as the subtask.'))

        return quality_issue
