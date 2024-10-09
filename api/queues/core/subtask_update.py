from typing import List

from api.models import SubtaskUpdate


def delete_on_location_matrix_delete(location_matrices_ids: List[int], context) -> None:
    from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

    subtasks_updates = SubtaskUpdateEntityService().get_subtasks_updates_for_subtasks_removing(
        location_matrices_ids=location_matrices_ids, user=context['request'].user
    )
    if subtasks_updates:
        SubtaskUpdateEntityService().create_many(
            validated_data=subtasks_updates,
            user=context['request'].user,
            project_pk=context['project_pk']
        )


def send_email_notification_about_created_subtask(subtask_update):
    from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

    SubtaskUpdateEntityService().send_email_about_created_subtask(subtask_update)


def send_email_notification_about_changed_subtask_status(subtask_update: SubtaskUpdate):
    from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

    SubtaskUpdateEntityService().send_email_about_update(subtask_update)


def send_email_notification_about_created_comment(subtask_update: SubtaskUpdate):
    from api.services.subtask_update_entity_service import SubtaskUpdateEntityService

    SubtaskUpdateEntityService().send_email_about_update(subtask_update)
