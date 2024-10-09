from copy import deepcopy
from typing import List, Optional

import pendulum
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _

from api.http.serializers.subtask_update.subtask_update_new_data_serializer import SubtaskUpdateNewDataSerializer
from api.mails.subtask.comment_created import SubtaskCommentCreated
from api.mails.subtask.created import SubtaskCreated
from api.mails.subtask.statused import SubtaskStatusChanged
from api.models import Subtask, User, SubtaskUpdate, QualityIssue, Task, QualityIssueUpdate, LocationMatrixPackage
from api.queues.subtask_update import send_email_notification_about_changed_subtask_status, \
    send_email_notification_about_created_subtask, send_email_notification_about_created_comment
from api.queues.subtasks import recalculate_subtask_files_count, recalculate_subtask_closed_files_count
from api.services.base_entity_service import BaseEntityService
from api.services.floor_plan_area_pin_entity_service import FloorPlanAreaPinEntityService
from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService
from api.services.subtask_entity_service import SubtaskEntityService
from api.services.task_update_entity_service import TaskUpdateEntityService
from api.utilities.helpers import get_to_email_status_name
from api.utilities.status_flow.quality_issue_status_change_flow import QualityIssueStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import set_last_confirmed_update
from api.utilities.time_utilities import change_timezone_to_london
from api.utilities.update_history_utilities import sync_recipients


class SubtaskUpdateEntityService(BaseEntityService):
    model = SubtaskUpdate

    def create(
            self,
            validated_data,
            user: User = None,
            project_pk: int = None,
            sync_create: bool = True,
            comment_sync_create: bool = True,
            task_update_local_id: int = None,
            old_task_update_local_id: int = None,
            quality_issue_update_local_id: int = None,
            **kwargs
    ) -> SubtaskUpdate:
        floor_plan_area_pin = None
        if 'floor_plan_area_pin' in validated_data['new_data']:
            if validated_data['new_data']['floor_plan_area_pin'] is None:
                if deleting_floor_plan_area_pin := validated_data['subtask'].floor_plan_area_pin:
                    deleting_floor_plan_area_pin.delete()
            else:
                floor_plan_area_pin = FloorPlanAreaPinEntityService().create_or_update_from_subtask_update(
                    validated_data,
                    user=user
                )
                validated_data['new_data']['floor_plan_area_pin']['floor_plan_area'] = floor_plan_area_pin.floor_plan_area.pk
                validated_data['new_data']['floor_plan_area_pin']['id'] = floor_plan_area_pin.pk
                if 'content_type' in validated_data['new_data']['floor_plan_area_pin']:
                    del validated_data['new_data']['floor_plan_area_pin']['content_type']

        if 'command' in kwargs:
            old_status = validated_data.get('old_data', {}).get('status')
            if not validated_data.get('is_comment') and validated_data['subtask'].status != old_status:
                validated_data['is_conflict'] = True
                kwargs.get('command').mark_as_conflicted()

        if validated_data.get('is_comment'):
            return self.create_comment(
                validated_data,
                sync_create=comment_sync_create,
                quality_issue_update_local_id=quality_issue_update_local_id
            )

        unchanged_validated_data = deepcopy(validated_data)
        unchanged_validated_data['local_id'] = quality_issue_update_local_id

        self._change_status_for_related_task(
            subtask_update=validated_data,
            user=user,
            old_task_update_local_id=old_task_update_local_id
        )

        if not validated_data.get('is_conflict', False):
            subtask_update_new_data_serializer = SubtaskUpdateNewDataSerializer(
                validated_data['subtask'],
                data=validated_data['new_data'],
                context={'project_pk': project_pk}
            )
            subtask_update_new_data_serializer.is_valid(raise_exception=True)
            validated_new_data = subtask_update_new_data_serializer.validated_data.copy()

            if 'floor_plan_area_pin' in validated_new_data:
                del validated_new_data['floor_plan_area_pin']

            SubtaskEntityService().update(
                instance=subtask_update_new_data_serializer.instance,
                validated_data=validated_new_data,
                task_update_local_id=task_update_local_id
            )

            def does_subtask_files_count_changed() -> bool:
                return (
                    validated_new_data.get('files')
                    and subtask_update_new_data_serializer.instance.files.count()
                    != len(validated_new_data['files'])
                )

            if does_subtask_files_count_changed():
                connection = transaction.get_connection()
                if connection.in_atomic_block:
                    transaction.on_commit(lambda: recalculate_subtask_files_count(subtask_update_new_data_serializer.instance))
                else:
                    recalculate_subtask_files_count(subtask_update_new_data_serializer.instance)

        recipients = validated_data.pop('recipients', [])
        subtask_update = super().create(validated_data)

        if validated_data['new_data']['status'] == Subtask.Status.CLOSED.value:
            connection = transaction.get_connection()
            if connection.in_atomic_block:
                transaction.on_commit(lambda: recalculate_subtask_closed_files_count(validated_data['subtask']))
            else:
                recalculate_subtask_closed_files_count(validated_data['subtask'])

        if sync_create:
            if floor_plan_area_pin:
                del unchanged_validated_data['new_data']['floor_plan_area_pin']

            self._add_quality_issue_location_change_to_update(
                subtask=validated_data['subtask'],
                update=unchanged_validated_data
            )

            QualityIssueUpdateEntityService().sync_create(validated_data=unchanged_validated_data, user=user)

        set_last_confirmed_update(subtask_update, user)
        sync_recipients(subtask_update, recipients)

        if subtask_update.subtask.subtaskupdate_set.count() > 1:
            send_email_notification_about_changed_subtask_status(subtask_update)
        else:
            send_email_notification_about_created_subtask(subtask_update)

        return subtask_update

    def create_comment(self, validated_data: dict, sync_create: bool = True, quality_issue_update_local_id: str = None) -> SubtaskUpdate:
        validated_data['new_data'] = {}
        validated_data['old_data'] = {}
        recipients = validated_data.pop('recipients', [])
        update = super().create(validated_data)

        setattr(validated_data['subtask'], 'updated_at', pendulum.now())
        validated_data['subtask'].save(update_fields=['updated_at'])

        sync_recipients(update, recipients)
        quality_issue = validated_data['subtask'].quality_issue

        if sync_create and quality_issue and not update.user.is_subcontractor:
            QualityIssueUpdateEntityService().comment_sync_create(update, quality_issue_update_local_id)

        send_email_notification_about_created_comment(update)

        return update

    def create_from_quality_issue_updates(self, subtask: Subtask) -> None:
        qi_updates = subtask.quality_issue.qualityissueupdate_set.all()

        for qi_update in qi_updates:
            serialized_update = {
                'comment': qi_update.comment,
                'subtask': subtask,
                'old_data': qi_update.old_data,
                'new_data': qi_update.new_data,
                'user': qi_update.user,
                'local_id': None,
                'files': qi_update.files.values_list('id', flat=True)
            }
            super().create(serialized_update)

    def comment_sync_create(self, quality_issue_update: QualityIssueUpdate, local_id: str = None) -> None:
        subtask = quality_issue_update.quality_issue.subtask_set.first()
        self.create_comment({
            'comment': quality_issue_update.comment,
            'subtask': subtask,
            'user': quality_issue_update.user,
            'is_comment': True,
            'files': quality_issue_update.files.values_list('id', flat=True),
            'local_id': local_id
        }, sync_create=False)

    def _change_status_for_related_task(
            self,
            user: User,
            subtask_update: dict,
            old_task_update_local_id: Optional[int]
    ) -> None:
        def is_task_changed() -> bool:
            return subtask_update['new_data'].get('task') != subtask_update['subtask'].task.id

        def does_task_has_only_one_subtask() -> bool:
            return subtask_update['subtask'].task.subtask_set.count() == 1

        if subtask_update['new_data'].get('task') and is_task_changed() and does_task_has_only_one_subtask():
            TaskUpdateEntityService().create({
                'task': subtask_update['subtask'].task,
                'user': user,
                'comment': subtask_update.get('comment'),
                'old_data': {'status': subtask_update['subtask'].task.status},
                'new_data': {'status': Task.Statuses.OUTSTANDING.value},
                'local_id': old_task_update_local_id
            })

    def sync_create(self, validated_data, user: User, task_update_local_id: Optional[int]) -> None:
        def does_need_to_copy_all() -> bool:
            return quality_issue_status_flow.is_requested_approval_rejected() or \
                   quality_issue_status_flow.is_multiplex_requesting_approval() or \
                   quality_issue_status_flow.is_requested_approval_rejected_update() or \
                   quality_issue_status_flow.is_contest()

        # New quality issue creating
        if 'status' not in validated_data['old_data']:
            return

        if QualityIssue.Status.UNDER_REVIEW in (validated_data['old_data']['status'], validated_data['new_data']['status']):
            return

        subtasks = validated_data['quality_issue'].subtask_set.all()
        quality_issue_status_flow = QualityIssueStatusChangeFlow(validated_data, user)
        recipients = validated_data.pop('recipients', [])

        for subtask in subtasks:
            update = {
                'user': user,
                'old_data': {'status': subtask.status},
                'new_data': {'status': validated_data['new_data']['status']},
                'subtask': subtask,
                'local_id': validated_data['local_id']
            }

            if does_need_to_copy_all():
                update['comment'] = validated_data.get('comment')
                update['files'] = validated_data.get('files', [])

            SubtaskEntityService().update(
                instance=subtask,
                validated_data=update['new_data'],
                task_update_local_id=task_update_local_id
            )

            subtask_update = super().create(validated_data=update)
            sync_recipients(update_entity=subtask_update, recipients=recipients)
            set_last_confirmed_update(entity_update=subtask_update, user=user)

            if update['new_data']['status'] == Subtask.Status.CLOSED.value:
                recalculate_subtask_closed_files_count(subtask)

    def get_subtasks_updates_for_subtasks_removing(self, location_matrices_ids: List[int], user: User) -> List[dict]:
        subtasks = Subtask.objects.filter(
            ~Q(status__in=[Subtask.Status.CLOSED, Subtask.Status.REMOVED]),
            task__location_matrix_id__in=location_matrices_ids
        )
        return list(map(lambda subtask: {
            'subtask': subtask,
            'user': user,
            'old_data': {
                'status': subtask.status
            },
            'new_data': {
                'status': Subtask.Status.REMOVED
            },
        }, subtasks))

    def send_email_about_created_subtask(self, subtask_update: SubtaskUpdate) -> None:
        def get_subject():
            return _('MBuild – Urgent Attention, Immediate Response Required - %s, %s - %s - %s' % (
            project_name, building, level, area)) \
                if len(to_recipients) > 0 \
                else _('MBuild – Rework & Defect Notice - %s, %s - %s - %s' % (project_name, building, level, area))

        subtask = subtask_update.subtask
        task = subtask.task
        subtask_update_user = subtask_update.user
        location_matrix = task.location_matrix

        due_date = ''
        if subtask.due_date:
            due_date = change_timezone_to_london(subtask.due_date)
            due_date = pendulum.from_timestamp(due_date.timestamp()).strftime('%b %d, %Y %I:%m %p')

        building = location_matrix.building
        area = location_matrix.area
        level = location_matrix.level

        project_name = location_matrix.project.name
        package_name = LocationMatrixPackage.all_objects.filter(
            location_matrix=location_matrix,
            package_activity__pk=task.package_activity.pk
        ).get().package.name

        package_activity_name = task.package_activity.name
        package_activity_task_description = task.package_activity_task.description

        app_url = settings.APP_URL

        links = [
            {'name': 'Photo ' + str(num),
             'url': app_url + reverse('media_private_retrieve', kwargs={'uuid': file.hash})}
            for num, file in enumerate(subtask_update.files.all(), start=1)
        ]

        to_recipients = [recipient.email for recipient in subtask_update.recipients.all()]
        to_multiplex = list(
            User.objects.filter(
                Q(Q(groups=User.Group.COMPANY_ADMIN.value) | Q(is_superuser=True)) & ~Q(email__in=to_recipients)
            ).distinct().values_list('email', flat=True)
        )
        has_subcontractor_in_recipients = User.objects.filter(
            groups=User.Group.SUBCONTRACTOR.value,
            email__in=to_recipients
        ).exists()

        context = {
            'area': area,
            'due_date': due_date,
            'building': building,
            'id': subtask.id,
            'level': level,
            'links': links,
            'package_activity_name': package_activity_name,
            'package_activity_task_description': package_activity_task_description,
            'package_name': package_name,
            'project_name': project_name,
            'subtask_update_user': subtask_update_user,
            'update': subtask_update,
        }

        SubtaskCreated() \
            .set_subject(get_subject()) \
            .set_to(to_multiplex) \
            .set_reply_to(subtask_update_user.email) \
            .set_context(context) \
            .send()

        if len(to_recipients) > 0:
            SubtaskCreated() \
                .set_subject(get_subject()) \
                .set_to(to_recipients) \
                .set_reply_to(subtask_update_user.email) \
                .set_context({**context, 'has_subcontractor_in_recipients': has_subcontractor_in_recipients}) \
                .send()

    def send_email_about_update(self, subtask_update: SubtaskUpdate) -> None:
        def get_subject():
            return (
                _('MBuild – Urgent Attention, Immediate Response Required - %s, %s - %s - %s' %
                  (project_name, building, level, area))
                if len(to_recipients) > 0
                else _('MBuild – Rework & Defect Statused - %s, %s - %s - %s' % (project_name, building, level, area))
            )

        subtask = subtask_update.subtask
        app_url = settings.APP_URL
        task = subtask.task
        location_matrix = task.location_matrix
        building = location_matrix.building
        level = location_matrix.level
        area = location_matrix.area
        project = location_matrix.project

        to_recipients = [recipient.email for recipient in subtask_update.recipients.all()]
        to_multiplex = list(User.objects.filter(Q(Q(is_superuser=True) | Q(groups=User.Group.COMPANY_ADMIN.value)) &
                                                ~Q(email__in=to_recipients)).all().values_list('email', flat=True))
        has_subcontractor_in_recipients = User.objects.filter(groups=User.Group.SUBCONTRACTOR.value,
                                                              email__in=to_recipients).exists()
        status = self._get_status(subtask_update, subtask)
        status_name = get_to_email_status_name(Subtask, status)
        project_name = location_matrix.project.name
        try:
            package_name = location_matrix.locationmatrixpackage_set.filter(
                package_activity__pk=subtask.task.package_activity.pk
            ).get().package.name
        except LocationMatrixPackage.DoesNotExist:
            return

        package_activity_name = subtask.task.package_activity.name
        package_activity_task_description = subtask.task.package_activity_task.description

        links = [
            {'name': 'Photo ' + str(num),
             'url': app_url + reverse('media_private_retrieve', kwargs={'uuid': file.hash})}
            for num, file
            in enumerate(subtask_update.files.all(), start=1)
        ]

        due_date = ''
        if subtask.due_date:
            due_date = pendulum.from_timestamp(subtask.due_date.timestamp()).strftime('%b %d, %Y')

        context = {
            'area': area,
            'building': building,
            'level': level,
            'links': links,
            'status': status,
            'status_name': status_name,
            'subtask_update_comment': subtask_update.comment,
            'package_activity_name': package_activity_name,
            'package_activity_task_description': package_activity_task_description,
            'package_name': package_name,
            'project_name': project.name,
            'update_user': subtask_update.user,
            'update': subtask_update,
            'due_date': due_date,
            'qi_id': subtask.quality_issue_id
        }

        email_class = SubtaskCommentCreated() if subtask_update.is_comment else SubtaskStatusChanged()
        email_class \
            .set_subject(get_subject()) \
            .set_to(to_multiplex) \
            .set_reply_to(subtask_update.user.email) \
            .set_context(context) \
            .send()

        if len(to_recipients) > 0:
            email_class \
                .set_subject(get_subject()) \
                .set_to(to_recipients) \
                .set_reply_to(subtask_update.user.email) \
                .set_context({**context, 'has_subcontractor_in_recipients': has_subcontractor_in_recipients}) \
                .send()

    def _get_status(self, subtask_update: SubtaskUpdate, subtask: Subtask) -> str:
        if subtask_update.is_comment:
            return subtask.status

        return Subtask.Status.IN_PROGRESS.value \
            if subtask_update.new_data['status'] == Subtask.Status.INSPECTION_REJECTED \
            else subtask_update.new_data['status']

    def _add_quality_issue_location_change_to_update(self, subtask: Subtask, update: dict) -> None:
        if subtask.quality_issue and subtask.task.location_matrix.pk != subtask.quality_issue.location_matrix.pk:
            update['old_data']['location_matrix'] = subtask.quality_issue.location_matrix.pk
            update['new_data']['location_matrix'] = subtask.task.location_matrix.pk
