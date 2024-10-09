from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import User, Media, QualityIssueUpdate, QualityIssue, Project
from api.http.serializers.user.user_serializer import UserSerializer
from api.http.serializers import MediaSerializer
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.utilities.status_flow.quality_issue_status_change_flow import QualityIssueStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import get_last_update_with_changed_status
from .quality_issue_update_new_data_serializer import QualityIssueUpdateNewDataSerializer
from .. import RecipientSerializer


class QualityIssueUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = QualityIssueUpdate
        fields = (
            'id', 'quality_issue', 'user', 'comment', 'files', 'old_data', 'local_id',
            'new_data', 'created_at', 'updated_at', 'recipients', 'is_conflict', 'is_comment',
        )
        expandable_fields = {
            'expanded_recipients': (RecipientSerializer, {'many': True, 'source': 'recipients'}),
            'expanded_quality_issue': ('api.http.serializers.QualityIssueSerializer', {'source': 'quality_issue'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'}),
            'expanded_previous_status': (serializers.SerializerMethodField, {'method_name': 'previous_status'})
        }

    id = fields.ReadOnlyField()
    is_comment = serializers.BooleanField(required=False)
    quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    comment = fields.CharField(required=False, allow_null=True)
    files = serializers.PrimaryKeyRelatedField(required=False, queryset=Media.objects.all(), many=True,
                                               allow_null=False, allow_empty=True)
    old_data = fields.JSONField(required=True)
    new_data = fields.JSONField(required=False)
    recipients = RecipientSerializer(required=False, many=True)
    is_conflict = fields.BooleanField(required=False, default=False)
    local_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)

    def __init__(self, *args, **kwargs):
        self.allow_update_all_fields = kwargs.pop('allow_update_all_fields') if 'allow_update_all_fields' in kwargs else []
        super().__init__(*args, **kwargs)

    def previous_status(self, obj: QualityIssueUpdate):
        update_with_changed_status = get_last_update_with_changed_status(obj.quality_issue)

        return update_with_changed_status.old_data['status'] if update_with_changed_status else None

    def validate_recipients(self, recipients: list):
        if 'project_pk' in self.context and self.context['request'].user.is_client:
            def does_subcontractor_in_recipients():
                return Project.objects.filter(users__email__in=recipients_emails,
                                              users__group=User.Group.SUBCONTRACTOR.value).exists()

            recipients_emails = [recipient['email'] for recipient in recipients]
            if does_subcontractor_in_recipients():
                raise ValidationError(_('You cannot notify subcontractors about updates.'))

        return recipients

    def validate(self, validated_data):
        if validated_data.get('is_comment'):
            self._validate_comment(validated_data)
        else:
            self._validate_update(validated_data)
            self._validate_new_data(validated_data)
            self._validate_status_flow(validated_data)

        return validated_data

    def _validate_status_flow(self, data: dict) -> None:
        def does_need_to_update_due_date():
            return (user.is_client or user.is_consultant) and \
                   quality_issue.is_contested and \
                   not status_flow.is_remove() and \
                   not status_flow.is_update() and \
                   'due_date' not in data['new_data']

        def reject_description_change_for_client_and_consultant():
            return (user.is_client or user.is_consultant) and \
                   new_data.get('description', '') != old_data.get('description', '') and \
                   not (quality_issue.is_under_review or
                        quality_issue.is_contested or
                        quality_issue.is_requesting_approval)

        user = self.context['request'].user
        new_data = data.get('new_data', {})
        old_data = data.get('old_data', {})
        quality_issue = data['quality_issue']
        status_flow = QualityIssueStatusChangeFlow(data, user)

        if not status_flow.is_valid_change():
            raise ValidationError({'status': _('You cannot change status from %s to %s.' % (old_data.get('status'),
                                                                                            new_data.get('status'),))})
        if does_need_to_update_due_date():
            raise ValidationError({'due_date': _('You should set the Due date.')})

        if reject_description_change_for_client_and_consultant():
            raise ValidationError(
                {'description': _('You can change description for the quality issue only in status %s or %s.' % (
                    QualityIssue.Status.UNDER_REVIEW, QualityIssue.Status.CONTESTED))})

    def _validate_new_data(self, validated_data: dict) -> None:
        quality_issue = validated_data['quality_issue']
        exclude_fields = [] if self._allow_update_all_fields(quality_issue) else ['attachments']
        qi_update_new_data_serializer = QualityIssueUpdateNewDataSerializer(
            quality_issue,
            data=validated_data['new_data'],
            exclude_fields=exclude_fields
        )
        qi_update_new_data_serializer.is_valid(raise_exception=True)

        # todo Check on iOS client that the same validation exists
        #  to avoid conflicts between local and remote commands and events
        # valid_fields = qi_update_new_data_serializer.validated_data.keys()
        # for field in validated_data['new_data'].keys():
        #     if field in valid_fields:
        #         continue
        #
        #     del validated_data['new_data'][field]

    def _allow_update_all_fields(self, quality_issue: QualityIssue) -> bool:
        user = self.context['request'].user

        return self.allow_update_all_fields or \
            user.is_superuser or \
            ((user.is_client or user.is_consultant) and
             (quality_issue.is_contested or quality_issue.is_under_review or quality_issue.is_requesting_approval))

    def _validate_comment(self, validated_data: dict) -> None:
        service = QualityIssueEntityService()
        if service.is_comment_quality_issue_in_forbidden_statuses(validated_data['quality_issue']):
            raise ValidationError(_('You cannot create comment for quality issue in status '
                                    f'{QualityIssue.Status.CLOSED} or {QualityIssue.Status.REMOVED}.'))

        if service.is_comment_creation_for_quality_issue_forbidden(validated_data['quality_issue'], self.context['request'].user):
            raise PermissionError(_('You cannot create quality issue comment.'))

    def _validate_update(self, validated_data: dict) -> None:
        def restrict_due_date_update():
            return 'due_date' in validated_data['new_data'] and \
                   not (qi.is_contested or
                        qi.is_under_review or
                        qi.is_requesting_approval or
                        qi.is_requested_approval_rejected)

        qi = validated_data['quality_issue']

        if restrict_due_date_update():
            raise ValidationError(
                {'due_date': _('You can update the Due date only in statuses Contested and Under Review.')})
