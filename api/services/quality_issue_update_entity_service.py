from copy import deepcopy
from typing import Optional

import pendulum
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _

from api.http.serializers.quality_issue_update.quality_issue_update_new_data_serializer import QualityIssueUpdateNewDataSerializer
from api.mails import QualityIssueCreated
from api.mails.quality_issue.comment_created import QualityIssueCommentCreated
from api.mails.quality_issue.notify_owner import QualityIssueStatusChanged
from api.models import User, QualityIssueUpdate, QualityIssue, Subtask, SubtaskUpdate
from api.queues.quality_issue import send_email_notification_about_created_quality_issue_comment,\
    send_email_notification_about_changed_quality_issue_status
from api.services.base_entity_service import BaseEntityService
from api.services.floor_plan_area_pin_entity_service import FloorPlanAreaPinEntityService
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.utilities.helpers import get_to_email_status_name
from api.utilities.status_flow.subtask_status_change_flow import SubtaskStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import set_last_confirmed_update
from api.utilities.time_utilities import change_timezone_to_london
from api.utilities.update_history_utilities import sync_recipients


class QualityIssueUpdateEntityService(BaseEntityService):
    model = QualityIssueUpdate

    def create(
            self,
            validated_data: dict,
            subtask_update_local_id: int = None,
            task_update_local_id: int = None,
            comment_sync_create: bool = True,
            sync_create: bool = True,
            notify: bool = True,
            user: User = None,
            **kwargs
    ) -> QualityIssueUpdate:
        if 'command' in kwargs:
            old_status = validated_data.get('old_data', {}).get('status')
            if not validated_data.get('is_comment') and validated_data['quality_issue'].status != old_status:
                validated_data['is_conflict'] = True
                kwargs.get('command').mark_as_conflicted()

        if 'floor_plan_area_pin' in validated_data['new_data']:
            if validated_data['new_data']['floor_plan_area_pin'] is None:
                if deleting_floor_plan_area_pin := validated_data['quality_issue'].floor_plan_area_pin:
                    deleting_floor_plan_area_pin.delete()
            else:
                floor_plan_area_pin = FloorPlanAreaPinEntityService().create_or_update_from_quality_issue_update(
                    validated_data,
                    user=user
                )
                validated_data['new_data']['floor_plan_area_pin']['floor_plan_area'] = floor_plan_area_pin.floor_plan_area.id

        if validated_data.get('is_comment'):
            return self.create_comment(
                validated_data,
                sync_create=comment_sync_create,
                subtask_update_local_id=subtask_update_local_id
            )

        unchanged_validated_data = deepcopy(validated_data)

        quality_issue = validated_data['quality_issue']
        recipients = validated_data.pop('recipients', [])

        if not validated_data.get('is_conflict', False):
            serializer = QualityIssueUpdateNewDataSerializer(quality_issue, data=validated_data['new_data'])
            serializer.is_valid(raise_exception=True)
            validated_new_data = serializer.validated_data.copy()

            if 'floor_plan_area_pin' in validated_new_data:
                del validated_new_data['floor_plan_area_pin']

            QualityIssueEntityService().update(quality_issue, validated_new_data)

        quality_issue_update = super().create(validated_data)

        if sync_create:
            from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

            unchanged_validated_data['local_id'] = subtask_update_local_id

            if 'floor_plan_area_pin' in unchanged_validated_data['new_data']:
                del unchanged_validated_data['new_data']['floor_plan_area_pin']

            SubtaskUpdateEntityService().sync_create(
                user=user,
                validated_data=unchanged_validated_data,
                task_update_local_id=task_update_local_id
            )

        set_last_confirmed_update(quality_issue_update, user)
        sync_recipients(quality_issue_update, recipients)

        if notify and quality_issue.qualityissueupdate_set.count() > 1:
            send_email_notification_about_changed_quality_issue_status(quality_issue_update)

        return quality_issue_update

    def create_comment(self, validated_data: dict, sync_create: bool = True, subtask_update_local_id: str = None) -> QualityIssueUpdate:
        validated_data['new_data'] = {}
        validated_data['old_data'] = {}
        recipients = validated_data.pop('recipients', [])
        update = super().create(validated_data)
        setattr(validated_data['quality_issue'], 'updated_at', pendulum.now())
        validated_data['quality_issue'].save(update_fields=['updated_at'])

        sync_recipients(update, recipients)
        subtask = validated_data['quality_issue'].subtask_set.first()
        if sync_create and subtask:
            from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

            SubtaskUpdateEntityService().comment_sync_create(update, local_id=subtask_update_local_id)

        send_email_notification_about_created_quality_issue_comment(update)

        return update

    def comment_sync_create(self, subtask_update: SubtaskUpdate, local_id: str = None) -> None:
        quality_issue = subtask_update.subtask.quality_issue
        self.create_comment({
            'comment': subtask_update.comment,
            'quality_issue': quality_issue,
            'user': subtask_update.user,
            'is_comment': True,
            'files': subtask_update.files.values_list('id', flat=True),
            'local_id': local_id
        }, sync_create=False)

    def sync_create(self, validated_data: dict, user: User) -> None:
        def is_full_data_copy_allowed() -> bool:
            return SubtaskStatusChangeFlow(
                update=validated_data, user=user
            ).is_sync_create_full_data_copy_allowed()

        def is_update_files_copy_allowed() -> bool:
            return SubtaskStatusChangeFlow(
                update=validated_data, user=user
            ).is_sync_create_update_files_copy_allowed()

        if validated_data['subtask'].quality_issue:
            qi = validated_data['subtask'].quality_issue
            old_data = {'status': qi.status}
            new_data = {'status': validated_data['new_data']['status']}

            if validated_data['new_data'].get('description'):
                old_data['description'] = qi.description
                new_data['description'] = validated_data['new_data']['description']

            if validated_data['new_data'].get('location_matrix'):
                old_data['location_matrix'] = validated_data['old_data']['location_matrix']
                new_data['location_matrix'] = validated_data['new_data']['location_matrix']

            files = []

            if is_update_files_copy_allowed():
                for media in validated_data.get('files', []):
                    media = media if type(media) is int else media.pk
                    files.append(media)

            comment = None
            if is_full_data_copy_allowed():
                comment = validated_data.get('comment')
                if validated_data['new_data'].get('files'):
                    new_attachments = []

                    for media in validated_data['new_data']['files']:
                        media = media if type(media) is int else media.pk
                        new_attachments.append(media)

                    old_data['attachments'] = list(qi.attachments.all().values_list('pk', flat=True))
                    new_data['attachments'] = new_attachments

            update = {
                'user': user,
                'old_data': old_data,
                'new_data': new_data,
                'quality_issue': qi,
                'comment': comment,
                'is_comment': validated_data.get('is_comment', False),
                'is_conflict': validated_data.get('is_conflict', False),
                'files': files,
                'local_id': validated_data.get('local_id')
            }

            if not validated_data.get('is_conflict', False):
                qi_update_new_data_serializer = QualityIssueUpdateNewDataSerializer(qi, data=update['new_data'],
                                                                                    status_sync=True)
                qi_update_new_data_serializer.is_valid(raise_exception=True)

                self.update(
                    qi_update_new_data_serializer.instance,
                    qi_update_new_data_serializer.validated_data
                )

            quality_issue_update = super().create(update)
            recipients = validated_data.pop('recipients', [])

            sync_recipients(quality_issue_update, recipients)

            if not validated_data.get('is_conflict', False):
                set_last_confirmed_update(quality_issue_update, user)

    def create_note_that_quality_issue_based_on_another(
            self,
            user: User,
            quality_issue: QualityIssue,
            validated_data: dict,
            reopen_note_quality_issue_update_local_id: Optional[int]
    ) -> None:
        update_data = self.__get_update_data_for_note_that_quality_issue_based_on_another(
            quality_issue=quality_issue,
            old_quality_issue=validated_data['old_quality_issue'],
            reopen_note_quality_issue_update_local_id=reopen_note_quality_issue_update_local_id
        )

        self.create(update_data, notify=False, user=user)

    def replace_data_from_subtask(
            self,
            subtask: Subtask,
            user: User,
            quality_issue_update_local_id: Optional[int]
    ) -> None:
        qi = subtask.quality_issue
        old_data = {'status': qi.status}
        new_data = {'status': subtask.status}
        files = []
        new_attachments = list(subtask.files.all().values_list('id', flat=True))

        if subtask.description:
            old_data['description'] = qi.description
            new_data['description'] = subtask.description

        if new_attachments:
            old_data['attachments'] = list(qi.attachments.all().values_list('id', flat=True))
            new_data['attachments'] = new_attachments
            files = new_attachments

        if subtask.task.location_matrix.pk != qi.location_matrix.pk:
            old_data['location_matrix'] = qi.location_matrix.pk
            new_data['location_matrix'] = subtask.task.location_matrix.pk

        quality_issue_update = {
            'quality_issue': qi,
            'old_data': old_data,
            'new_data': new_data,
            'files': files,
            'user': user,
            'local_id': quality_issue_update_local_id
        }

        self.create(validated_data=quality_issue_update, sync_create=False, user=user)

    def change_status_to_in_progress(
            self,
            user: User,
            quality_issue: QualityIssue,
            quality_issue_update_local_id: Optional[int]
    ) -> Optional[QualityIssueUpdate]:
        if quality_issue.is_in_progress:
            return

        return self._change_status(
            user=user,
            quality_issue=quality_issue,
            status=QualityIssue.Status.IN_PROGRESS,
            quality_issue_update_local_id=quality_issue_update_local_id
        )

    def change_status_to_removed(
            self,
            user: User,
            quality_issue: QualityIssue,
            quality_issue_update_local_id: Optional[int]
    ) -> Optional[QualityIssueUpdate]:
        if quality_issue.is_removed:
            return

        return self._change_status(
            user=user,
            quality_issue=quality_issue,
            status=QualityIssue.Status.REMOVED,
            quality_issue_update_local_id=quality_issue_update_local_id
        )

    def send_email_about_created_quality_issue(self, quality_issue_update: QualityIssueUpdate) -> None:
        def get_subject():
            return _('MBuild – Urgent Attention, Immediate Response Required – %s, %s - %s - %s' % (
            project.name, building, level, area)) \
                if len(to_recipients) > 0 \
                else _('MBuild – Quality Issue Notice – %s, %s - %s - %s' % (project.name, building, level, area))

        quality_issue = quality_issue_update.quality_issue
        location_matrix = quality_issue.location_matrix
        building = location_matrix.building
        level = location_matrix.level
        area = location_matrix.area
        project = location_matrix.project

        to_recipients = [recipient.email for recipient in quality_issue_update.recipients.all()]
        to_multiplex = list(User.objects.filter(Q(Q(is_superuser=True) | Q(group=User.Group.COMPANY_ADMIN.value)) &
                                                ~Q(email__in=to_recipients)).all().values_list('email', flat=True))
        has_subcontractor_in_recipients = User.objects.filter(group=User.Group.SUBCONTRACTOR.value,
                                                              email__in=to_recipients).exists()
        raised_by = '%s %s' % (quality_issue.user.first_name, quality_issue.user.last_name)

        app_url = settings.APP_URL

        links = [
            {'name': 'Photo ' + str(num),
             'url': app_url + reverse('media_private_retrieve', kwargs={'uuid': file.hash})}
            for num, file
            in enumerate(quality_issue_update.files.all(), start=1)
        ]

        remaining_to_due_date = quality_issue.due_date - pendulum.now()
        due_date = change_timezone_to_london(quality_issue.due_date)
        due_date = pendulum.from_timestamp(due_date.timestamp()).strftime('%b %d, %Y')
        context = {
            'area': area,
            'building': building,
            'company': quality_issue.user.company.name,
            'description': quality_issue.description,
            'due_date': due_date,
            'email': quality_issue.user.email,
            'first_name': quality_issue.user.first_name,
            'last_name': quality_issue.user.last_name,
            'level': level,
            'links': links,
            'phone': quality_issue.user.phone,
            'project_name': project.name,
            'quality_issue_id': quality_issue.pk,
            'raised_by': raised_by,
            'remaining_to_due_date': remaining_to_due_date.days
        }

        QualityIssueCreated() \
            .set_subject(get_subject()) \
            .set_to(to_multiplex) \
            .set_context(context) \
            .send()

        if len(to_recipients) > 0:
            QualityIssueCreated() \
                .set_subject(get_subject()) \
                .set_to(to_recipients) \
                .set_context({**context, 'has_subcontractor_in_recipients': has_subcontractor_in_recipients}) \
                .send()

    def send_email_about_update(self, quality_issue_update: QualityIssueUpdate) -> None:
        def get_subject():
            return _('MBuild – Urgent Attention, Immediate Response Required – %s, %s - %s - %s' % (
            project.name, building, level, area)) \
                if len(to_recipients) > 0 \
                else _('MBuild – Rework & Defect Statused – %s, %s - %s - %s' % (project.name, building, level, area))

        quality_issue = quality_issue_update.quality_issue
        app_url = settings.APP_URL
        location_matrix = quality_issue.location_matrix
        building = location_matrix.building
        level = location_matrix.level
        area = location_matrix.area
        project = location_matrix.project

        to_recipients = [recipient.email for recipient in quality_issue_update.recipients.all()]
        to_multiplex = list(User.objects.filter(Q(Q(is_superuser=True) | Q(group=User.Group.COMPANY_ADMIN.value)) &
                                                ~Q(email__in=to_recipients)).all().values_list('email', flat=True))
        has_subcontractor_in_recipients = User.objects.filter(groups=User.Group.SUBCONTRACTOR.value,
                                                              email__in=to_recipients).exists()
        subtask = quality_issue.subtask_set.order_by('id').first()
        status = quality_issue.status if quality_issue_update.is_comment else quality_issue_update.new_data['status']
        status_name = get_to_email_status_name(QualityIssue, status)
        package_name = None
        package_activity_name = None
        package_activity_task_description = None
        if subtask:
            package_name = location_matrix.locationmatrixpackage_set.all_with_deleted().get(
                package_activity__pk=subtask.task.package_activity.pk
            ).package.name

            package_activity_name = subtask.task.package_activity.name
            package_activity_task_description = subtask.task.package_activity_task.description

        links = [
            {'name': 'Photo ' + str(num),
             'url': app_url + reverse('media_private_retrieve', kwargs={'uuid': file.hash})}
            for num, file
            in enumerate(quality_issue_update.files.all(), start=1)
        ]

        due_date = ''
        if quality_issue.due_date:
            if isinstance(quality_issue.due_date, str):
                due_date = pendulum.parse(quality_issue.due_date)
            else:
                due_date = pendulum.from_timestamp(quality_issue.due_date.timestamp())

            due_date = due_date.strftime('%b %d, %Y')

        context = {
            'area': area,
            'building': building,
            'level': level,
            'links': links,
            'status': status,
            'status_name': status_name,
            'package_activity_name': package_activity_name,
            'package_activity_task_description': package_activity_task_description,
            'package_name': package_name,
            'project_name': project.name,
            'update_user': quality_issue_update.user,
            'update': quality_issue_update,
            'due_date': due_date,
            'quality_issue_id': quality_issue.id
        }
        email_class = QualityIssueCommentCreated() if quality_issue_update.is_comment else QualityIssueStatusChanged()
        email_class \
            .set_subject(get_subject()) \
            .set_to(to_multiplex) \
            .set_context(context) \
            .send()

        if len(to_recipients) > 0:
            email_class \
                .set_subject(get_subject()) \
                .set_to(to_recipients) \
                .set_context({**context, 'has_subcontractor_in_recipients': has_subcontractor_in_recipients}) \
                .send()

    def _change_status(
            self,
            quality_issue: QualityIssue,
            status: QualityIssue.Status,
            user: User,
            quality_issue_update_local_id: Optional[int]
    ) -> QualityIssueUpdate:
        old_data = {'status': quality_issue.status}
        new_data = {'status': status}

        return self.create({
            'new_data': new_data,
            'old_data': old_data,
            'quality_issue': quality_issue,
            'user': user,
            'local_id': quality_issue_update_local_id
        }, notify=False, user=user)

    def __get_update_data_for_note_that_quality_issue_based_on_another(
            self,
            quality_issue: QualityIssue,
            old_quality_issue: QualityIssue,
            reopen_note_quality_issue_update_local_id: Optional[int]
    ) -> dict:
        old_quality_issue_rework = old_quality_issue.subtask_set.order_by('-created_at').first()
        comment = 'Quality Issue was created based on Q-%s%s.' % (old_quality_issue.pk,
                                                                  f' (R-{old_quality_issue_rework.pk})'
                                                                  if old_quality_issue_rework else '')
        return {
            'comment': comment,
            'quality_issue': quality_issue,
            'user': quality_issue.user,
            'local_id': reopen_note_quality_issue_update_local_id,
            'old_data': {
                'status': quality_issue.status
            },
            'new_data': {
                'status': quality_issue.status
            }
        }
