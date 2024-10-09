from copy import deepcopy
from functools import reduce
from typing import Optional

from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
import pendulum
from rest_framework.exceptions import ValidationError
from sentry_sdk import capture_exception

from api.models import Subtask, Task, QualityIssue, User, LocationMatrixPackage
from api.queues.subtasks import recalculate_subtask_files_count
from api.services.base_entity_service import BaseEntityService
from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService
from api.services.task_update_entity_service import TaskUpdateEntityService
from api.utilities.custom_exceptions import DuplicatedSubtaskError
from api.utilities.recipients_utilities import prepare_recipients


class SubtaskEntityService(BaseEntityService):
    model = Subtask

    def create(
            self,
            validated_data: dict,
            project_pk: int = None,
            user: User = None,
            task_update_local_id: int = None,
            subtask_update_local_id: int = None,
            quality_issue_update_local_id: int = None,
            **kwargs
    ) -> Subtask:
        floor_plan_area_pin = validated_data.pop('floor_plan_area_pin', None)
        validated_data['status'] = Subtask.Status.IN_PROGRESS
        recipients = validated_data.pop('recipients', [])
        project = validated_data['task'].location_matrix.project
        project_cd = pendulum.parse(str(project.completion_date))
        validated_data['building'] = validated_data['task'].building
        validated_data['level'] = validated_data['task'].level
        validated_data['area'] = validated_data['task'].area
        validated_data['project'] = project

        quality_issue = validated_data.get('quality_issue')
        if quality_issue and quality_issue.due_date:
            validated_data['response_due_date'] = quality_issue.due_date

        if pendulum.now().diff(project_cd, False).in_days() <= 0:
            validated_data['is_defect'] = True

        try:
            if quality_issue and self.model.objects.filter(quality_issue=quality_issue).exists():
                raise DuplicatedSubtaskError
        except DuplicatedSubtaskError as exc:
            capture_exception(exc)

        subtask = super().create(validated_data)

        if subtask.task.status != Task.Statuses.REJECTED and not subtask.is_closed:
            self._update_related_task_status(subtask, Task.Statuses.REJECTED, task_update_local_id)

        if validated_data.get('quality_issue'):
            from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

            SubtaskUpdateEntityService().create_from_quality_issue_updates(subtask)

        self._create_subtask_update(
            user=user,
            subtask=subtask,
            recipients=recipients,
            project_pk=project_pk,
            subtask_update_local_id=subtask_update_local_id,
            quality_issue_update_local_id=quality_issue_update_local_id,
            floor_plan_area_pin=floor_plan_area_pin
        )

        # Subtasks may be created from clients commands.
        # In this case, all operation wrapped in transaction.
        # To avoid transaction block add delayed calling.
        connection = transaction.get_connection()
        if connection.in_atomic_block:
            transaction.on_commit(lambda : recalculate_subtask_files_count(subtask))
        else:
            recalculate_subtask_files_count(subtask)

        return subtask

    def recalculate_subtask_files_count(self, subtask: Subtask) -> None:
        subtask.files_count = subtask.files.count()
        subtask.save(update_fields=['files_count'])

    def recalculate_subtask_closed_files_count(self, subtask: Subtask) -> None:
        if not subtask.is_closed:
            return None

        subtask_updates = subtask.subtaskupdate_set.prefetch_related('files').filter(
            new_data__status=Subtask.Status.CLOSED
        )

        subtask.closed_files_count = reduce(lambda count, update: count + update.files.count(), subtask_updates, 0)
        subtask.save(update_fields=['closed_files_count'])

    def bulk_create_from_quality_issues(self, validated_data: dict) -> list:
        quality_issues = set(validated_data.pop('quality_issues', []))
        subtasks = list()

        for quality_issue in quality_issues:
            subtask_data = dict()
            subtask_data['task'] = validated_data['task']
            subtask_data['user'] = validated_data['user']
            subtask_data['company'] = validated_data['company']
            subtask_data['quality_issue'] = quality_issue
            subtask_data['status'] = Subtask.Status.IN_PROGRESS
            subtask_data['due_date'] = pendulum.now().add(days=3)
            subtask_data['description'] = quality_issue.description
            subtask_data['files'] = [file.id for file in quality_issue.attachments.all()]
            subtasks.append(subtask_data)

        return self.create_many(subtasks, user=validated_data['user'])

    def bulk_create_from_tasks(self, validated_data: dict, user: User) -> list:
        tasks = validated_data.pop('tasks')
        subtasks = list()

        for task in tasks:
            subtask_data = validated_data.copy()
            subtask_data['task'] = task

            subtasks.append(subtask_data)

        return self.create_many(subtasks, user=user)

    def update(self, instance: Subtask, validated_data: dict, task_update_local_id: int = None, **kwargs) -> Subtask:
        update_data = deepcopy(validated_data)
        self._set_date_of_completion(instance, update_data)
        result = super().update(instance, update_data)
        self._change_status_of_related_task_depending_on_count_opened_subtasks(instance, task_update_local_id)

        return result

    def after_destroy(self, instance) -> None:
        self._change_status_of_related_task_depending_on_count_opened_subtasks(instance, None)

    def is_comment_subtask_in_forbidden_statuses(self, subtask: Subtask) -> bool:
        return subtask.is_closed or subtask.is_removed

    def delete_for_hidden_package_activity_task(self, tasks: list[Task]) -> None:
        task_chunks = [tasks[i:i + 500] for i in range(0, len(tasks), 500)]

        for task_chunk in task_chunks:
            Subtask.objects.filter(task_id__in=[task.id for task in task_chunk]).delete()

    def restore_for_shown_package_activity_task(self, activity_task_pk: int, project_pk: int) -> None:
        Subtask.deleted_objects.filter(
            Exists(LocationMatrixPackage.objects.filter(
                package_activity_id=OuterRef('task__package_activity_id'),
                location_matrix_id=OuterRef('task__location_matrix_id'),
                enabled=True
            )),
            task__package_activity_task_id=activity_task_pk,
            task__location_matrix__deleted__isnull=True,
            task__location_matrix__project__id=project_pk
        ).update(deleted=None)

    def restore_from_tasks(self, tasks: list[Task]) -> None:
        task_chunks = [tasks[i:i + 500] for i in range(0, len(tasks), 500)]

        for task_chunk in task_chunks:
            Subtask.deleted_objects.filter(task_id__in=[task.id for task in task_chunk]).update(deleted=None)

    def _create_subtask_update(
            self,
            subtask: Subtask,
            recipients: list,
            project_pk: int,
            user: User,
            subtask_update_local_id: Optional[int],
            quality_issue_update_local_id: Optional[int],
            floor_plan_area_pin: Optional[dict]
    ) -> None:
        from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

        subtask_update_data = self._prepare_subtask_update_data(
            subtask=subtask,
            recipients=recipients,
            subtask_update_local_id=subtask_update_local_id,
            floor_plan_area_pin=floor_plan_area_pin
        )

        self._replace_related_quality_issue_data(
            subtask=subtask,
            user=user,
            quality_issue_update_local_id=quality_issue_update_local_id
        )

        use_sync_create = subtask.quality_issue_id is None
        SubtaskUpdateEntityService().create(
            validated_data=subtask_update_data,
            sync_create=use_sync_create,
            user=user,
            quality_issue_update_local_id=quality_issue_update_local_id,
            project_pk=project_pk
        )

    def _replace_related_quality_issue_data(
            self,
            subtask: Subtask,
            user: User,
            quality_issue_update_local_id: Optional[int]
    ) -> None:
        if subtask.quality_issue:
            if subtask.quality_issue.status in [QualityIssue.Status.CLOSED, QualityIssue.Status.REMOVED]:
                raise ValidationError({
                    'quality_issue': _('You cannot open rework for the quality issue in statuses %s and %s.' %
                                       (QualityIssue.Status.CLOSED, QualityIssue.Status.REMOVED,))
                })

            QualityIssueUpdateEntityService().replace_data_from_subtask(
                subtask=subtask,
                user=user,
                quality_issue_update_local_id=quality_issue_update_local_id
            )

    def _prepare_subtask_update_data(
            self,
            subtask: Subtask,
            recipients: list,
            subtask_update_local_id: Optional[int],
            floor_plan_area_pin: Optional[dict]
    ) -> dict:
        prepared_recipients = prepare_recipients(recipients)
        new_data = {
            'company': subtask.company.pk if subtask.company else None,
            'status': subtask.status
        }
        if floor_plan_area_pin:
            new_data.update(floor_plan_area_pin=floor_plan_area_pin)

        return {
            'comment': subtask.description,
            'subtask': subtask,
            'recipients': prepared_recipients,
            'files': [file.pk for file in subtask.files.all()],
            'user': subtask.user,
            'local_id': subtask_update_local_id,
            'old_data': {},
            'new_data': new_data
        }

    def _set_date_of_completion(self, subtask: Subtask, update_data: dict) -> None:
        if not subtask.is_closed and update_data.get('status') == Subtask.Status.CLOSED:
            update_data['date_of_completion'] = pendulum.now().to_datetime_string()

    def _change_status_of_related_task_depending_on_count_opened_subtasks(
            self,
            subtask: Subtask,
            task_update_local_id: Optional[int]
    ) -> None:
        are_opened_subtasks_exist = subtask.task.subtask_set.exclude(status__in=[
            Subtask.Status.CLOSED, Subtask.Status.REMOVED
        ]).exists()

        if are_opened_subtasks_exist and subtask.task.status != Task.Statuses.REJECTED:
            self._update_related_task_status(
                subtask=subtask,
                status=Task.Statuses.REJECTED,
                task_update_local_id=task_update_local_id
            )
        elif not are_opened_subtasks_exist and subtask.task.status == Task.Statuses.REJECTED:
            status = (
                Task.Statuses.NOT_APPLICABLE
                if subtask.task.package_activity_task.is_not_applicable_status_by_default
                else Task.Statuses.OUTSTANDING
            )
            self._update_related_task_status(
                subtask=subtask,
                status=status,
                task_update_local_id=task_update_local_id
            )

    def _update_related_task_status(
            self,
            subtask: Subtask,
            status: Task.Statuses,
            task_update_local_id: Optional[int]
    ) -> None:
        subtask.task.status = status
        subtask.task.user = subtask.user
        subtask.task.updated_at = pendulum.now()
        subtask.task.save(update_fields=['status', 'user', 'updated_at'])
        subtask.refresh_from_db()

        TaskUpdateEntityService().create({
            'task': subtask.task,
            'user': subtask.user,
            'comment': subtask.description,
            'old_data': {'status': subtask.task.status},
            'new_data': {'status': status},
            'local_id': task_update_local_id
        })
