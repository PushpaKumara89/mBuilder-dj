from api.http.serializers.task_update.task_update_new_data_serializer import TaskUpdateNewDataSerializer
from api.models import TaskUpdate, Task
from api.queues.task_update import send_task_status_changed_email_notification
from api.services.base_entity_service import BaseEntityService
from api.utilities.update_history_utilities import sync_recipients


class TaskUpdateEntityService(BaseEntityService):
    model = TaskUpdate

    def create(self, validated_data, **kwargs):
        if 'command' in kwargs:
            old_status = validated_data['old_data']['status']
            if validated_data['task'].status != old_status:
                validated_data['is_conflict'] = True
                kwargs.get('command').mark_as_conflicted()

        recipients = validated_data.pop('recipients', [])

        task_update_new_data_serializer = TaskUpdateNewDataSerializer(validated_data['task'], data=validated_data['new_data'])
        task_update_new_data_serializer.is_valid(raise_exception=True)

        if not validated_data.get('is_conflict', False):
            from api.services.task_entity_service import TaskEntityService

            TaskEntityService().update(task_update_new_data_serializer.instance, {
                **task_update_new_data_serializer.initial_data,
                'user': validated_data['user']
            })

        task_update = super().create(validated_data)

        sync_recipients(task_update, recipients)

        if task_update.new_data['status'] in [Task.Statuses.ACCEPTED, Task.Statuses.PART_COMPLETE]:
            send_task_status_changed_email_notification(task_update)

        return task_update

    def bulk_create(self, validated_data: dict) -> list:
        task_updates = validated_data.pop('task_updates', [])
        task_updates_data = []

        for task_update in task_updates:
            task_update['comment'] = validated_data['comment'] if 'comment' in validated_data else None
            task_update['recipients'] = validated_data['recipients'] if 'recipients' in validated_data else []
            task_update['files'] = validated_data['files'] if 'files' in validated_data else []
            task_update['user'] = validated_data['user']
            task_update['new_data'] = validated_data['new_data']
            task_updates_data.append(task_update)

        return self.create_many(task_updates_data)
