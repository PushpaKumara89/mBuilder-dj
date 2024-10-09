from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import User, Media, Subtask, SubtaskUpdate
from api.http.serializers.subtask.subtask_serializer import SubtaskSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.services.subtask_entity_service import SubtaskEntityService
from api.utilities.status_flow.subtask_status_change_flow import SubtaskStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import get_last_update_with_changed_status
from .subtask_update_new_data_serializer import SubtaskUpdateNewDataSerializer
from .. import RecipientSerializer, MediaSerializer


class SubtaskUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = SubtaskUpdate
        fields = (
            'id', 'subtask', 'user', 'comment', 'files', 'old_data', 'new_data', 'created_at', 'updated_at',
            'recipients', 'is_conflict', 'local_id', 'is_comment',
        )
        expandable_fields = {
            'expanded_subtask': (SubtaskSerializer, {'source': 'subtask'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'}),
            'expanded_recipients': (RecipientSerializer, {'many': True, 'source': 'recipients'}),
            'expanded_previous_status': (serializers.SerializerMethodField, {'method_name': 'previous_status'})
        }

    id = fields.ReadOnlyField()
    is_comment = serializers.BooleanField(required=False)
    subtask = serializers.PrimaryKeyRelatedField(queryset=Subtask.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    recipients = RecipientSerializer(required=False, many=True)
    comment = fields.CharField(required=False)
    files = serializers.PrimaryKeyRelatedField(required=False, queryset=Media.objects.all(), many=True,
                                               allow_null=False, allow_empty=True)
    old_data = fields.JSONField(required=True)
    new_data = fields.JSONField(required=False)
    is_conflict = fields.BooleanField(required=False, default=False)
    local_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)

    def previous_status(self, obj: SubtaskUpdate):
        if hasattr(obj.subtask, 'last_updates_with_changed_status'):
            update_with_changed_status = obj.subtask.last_updates_with_changed_status[0] if obj.subtask.last_updates_with_changed_status else None
        else:
            update_with_changed_status = get_last_update_with_changed_status(obj.subtask)

        return update_with_changed_status.old_data['status'] if update_with_changed_status else None

    def validate(self, validated_data: dict) -> dict:
        if validated_data.get('is_comment'):
            self._validate_comment(validated_data)
        else:
            self._validate_company(validated_data)
            self._validate_new_data(validated_data)
            self._validate_status_flow(validated_data)

        return validated_data

    def _validate_comment(self, validated_data: dict) -> None:
        if SubtaskEntityService().is_comment_subtask_in_forbidden_statuses(validated_data['subtask']):
            raise ValidationError(_('You cannot create comment for quality issue in status '
                                    f'{Subtask.Status.CLOSED} or {Subtask.Status.REMOVED}.'))

    def _validate_new_data(self, validated_data: dict) -> None:
        exclude_fields = [] if self._needed_to_include_fields(validated_data) else [
            'task', 'description', 'recipients', 'files', 'estimation', 'due_date'
        ]

        subtask_update_new_data_serializer = SubtaskUpdateNewDataSerializer(validated_data['subtask'],
                                                                            data=validated_data['new_data'],
                                                                            exclude_fields=exclude_fields,
                                                                            context=self.context)
        subtask_update_new_data_serializer.is_valid(raise_exception=True)

        # todo Check on iOS client that the same validation exists
        #  to avoid conflicts between local and remote commands and events
        # valid_fields = subtask_update_new_data_serializer.validated_data.keys()
        # for field in validated_data['new_data'].keys():
        #     if field in valid_fields:
        #         continue
        #
        #     del validated_data['new_data'][field]

    def _validate_company(self, validated_data: dict) -> None:
        subtask_company = validated_data['subtask'].company.pk if validated_data['subtask'].company else None
        is_company_changed = validated_data['new_data'].get('company') != subtask_company
        does_company_changing_by_non_staff = 'company' in validated_data['new_data'] and \
                                             not validated_data['user'].is_staff and \
                                             is_company_changed

        if does_company_changing_by_non_staff:
            raise ValidationError({'company': _('You\'re not allowed to change a company.')})

    def _validate_status_flow(self, data: dict) -> None:
        user = self.context['request'].user
        new_data = data['new_data']
        old_data = data['old_data']
        status_flow = SubtaskStatusChangeFlow(data, user)

        if not status_flow.is_valid_change():
            raise ValidationError({'status': _('You cannot change status from %s to %s.' % (old_data.get('status'),
                                                                                            new_data.get('status'),))})
    def _needed_to_include_fields(self, validated_data: dict) -> bool:
        return self.context['request'].user.is_superuser or \
               self.context['request'].user.is_staff or \
               validated_data['subtask'].is_contested or \
               validated_data['subtask'].is_removed or \
               validated_data['subtask'].is_closed or \
               validated_data['subtask'].is_declined or \
               (validated_data['subtask'].is_in_progress and self.context['request'].user.is_staff)
