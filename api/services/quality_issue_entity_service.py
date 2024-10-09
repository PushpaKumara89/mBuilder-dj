from copy import deepcopy
from typing import Optional

from django.db.models import Exists, OuterRef

from api.models import LocationMatrix, Project, QualityIssue, User, Task, LocationMatrixPackage
from api.queues.quality_issue import send_quality_issue_created_email_notification
from api.services.base_entity_service import BaseEntityService
from api.utilities.recipients_utilities import prepare_recipients


class QualityIssueEntityService(BaseEntityService):
    model = QualityIssue

    def create(
            self,
            validated_data,
            user: User = None,
            task_update_local_id: int = None,
            subtask_update_local_id: int = None,
            quality_issue_update_local_id: int = None,
            old_quality_issue_update_local_id: int = None,
            reopen_note_quality_issue_update_local_id: int = None,
            **kwargs
    ) -> QualityIssue:
        from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService

        quality_issue_update_service = QualityIssueUpdateEntityService()
        floor_plan_area_pin = validated_data.pop('floor_plan_area_pin', None)
        recipients = validated_data.pop('recipients', [])
        validated_data['status'] = QualityIssue.Status.UNDER_REVIEW.value

        quality_issue = super().create(validated_data)

        if validated_data.get('old_quality_issue'):
            quality_issue_update_service.change_status_to_removed(
                quality_issue=validated_data['old_quality_issue'],
                user=user,
                quality_issue_update_local_id=quality_issue_update_local_id
            )
            quality_issue_update_service.create_note_that_quality_issue_based_on_another(
                user=user,
                quality_issue=quality_issue,
                validated_data=validated_data,
                reopen_note_quality_issue_update_local_id=reopen_note_quality_issue_update_local_id
            )

        quality_issue_update_data = self._prepare_quality_issue_update_data(
            quality_issue=quality_issue,
            recipients=recipients,
            quality_issue_update_local_id=quality_issue_update_local_id,
            floor_plan_area_pin=floor_plan_area_pin
        )
        update = quality_issue_update_service.create(
            validated_data=quality_issue_update_data,
            user=user,
            subtask_update_local_id=subtask_update_local_id,
            task_update_local_id=task_update_local_id,
        )

        send_quality_issue_created_email_notification(update)

        return quality_issue

    def bulk_create(self, project: Project, validated_data: dict, user: User) -> list:
        area_filter = validated_data.pop('area', None)
        filters = {
            'project': project,
            'building': validated_data.pop('building'),
            'level': validated_data.pop('level')
        }
        if area_filter:
            filters['area__in'] = area_filter

        location_matrices = list(LocationMatrix.objects.filter(**filters))

        quality_issues = []

        for location_matrix in location_matrices:
            quality_issue = deepcopy(validated_data)
            quality_issue['location_matrix'] = location_matrix
            quality_issues.append(quality_issue)

        return self.create_many(quality_issues, user=user)

    def is_comment_quality_issue_in_forbidden_statuses(self, quality_issue: QualityIssue) -> bool:
        return quality_issue.is_closed or quality_issue.is_removed

    def is_comment_creation_for_quality_issue_forbidden(self, quality_issue: QualityIssue, user: User) -> bool:
        return (
            self.is_comment_creation_for_quality_issue_without_related_subtask_forbidden(quality_issue, user)
            or self.is_comment_creation_for_quality_issue_with_related_subtask_forbidden(quality_issue, user)
        )

    def delete_for_hidden_package_activity_task(self, tasks: list[Task]) -> None:
        task_chunks = [tasks[i:i + 500] for i in range(0, len(tasks), 500)]

        for task_chunk in task_chunks:
            QualityIssue.objects.filter(subtask__task_id__in=[task.id for task in task_chunk]).delete()

    def restore_for_shown_package_activity_task(self, activity_task_pk: int, project_pk: int) -> None:
        QualityIssue.deleted_objects.filter(
            Exists(LocationMatrixPackage.objects.filter(
                package_activity_id=OuterRef('subtask__task__package_activity_id'),
                location_matrix_id=OuterRef('subtask__task__location_matrix_id'),
                enabled=True
            )),
            subtask__task__package_activity_task_id=activity_task_pk,
            subtask__task__location_matrix__deleted__isnull=True,
            subtask__task__location_matrix__project__id=project_pk
        ).update(deleted=None)

    def restore_from_tasks(self, tasks):
        task_chunks = [tasks[i:i + 500] for i in range(0, len(tasks), 500)]

        for chunk in task_chunks:
            self.model.deleted_objects.filter(subtask__task_id__in=[task.id for task in chunk]).update(deleted=None)

    def is_comment_creation_for_quality_issue_without_related_subtask_forbidden(self, quality_issue: QualityIssue, user: User) -> bool:
        return (not quality_issue.subtask_set.exists()
                and quality_issue.status in [QualityIssue.Status.UNDER_REVIEW, QualityIssue.Status.CONTESTED]
                and user.group_id not in [User.Group.ADMIN.value, User.Group.MANAGER.value, User.Group.CLIENT.value,
                                       User.Group.CONSULTANT.value, User.Group.COMPANY_ADMIN.value])

    def is_comment_creation_for_quality_issue_with_related_subtask_forbidden(self, quality_issue: QualityIssue, user: User) -> bool:
        return (quality_issue.subtask_set.exists()
                and quality_issue.status in [QualityIssue.Status.CONTESTED, QualityIssue.Status.UNDER_INSPECTION,
                                             QualityIssue.Status.REQUESTING_APPROVAL, QualityIssue.Status.IN_PROGRESS,
                                             QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, QualityIssue.Status.DECLINED]
                and user.group_id not in [User.Group.CLIENT.value, User.Group.CONSULTANT.value])

    def _prepare_quality_issue_update_data(
            self,
            quality_issue: QualityIssue,
            recipients: list,
            quality_issue_update_local_id: Optional[int],
            floor_plan_area_pin: Optional[dict]
    ) -> dict:
        prepared_recipients = prepare_recipients(recipients)
        new_data = {
            'status': quality_issue.status
        }

        if floor_plan_area_pin:
            new_data['floor_plan_area_pin'] = floor_plan_area_pin

        return {
            'comment': quality_issue.description,
            'quality_issue': quality_issue,
            'recipients': prepared_recipients,
            'files': [file.pk for file in quality_issue.attachments.all()],
            'user': quality_issue.user,
            'old_data': {},
            'local_id': quality_issue_update_local_id,
            'new_data': new_data
        }
