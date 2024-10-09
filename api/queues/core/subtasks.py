from api.models.subtask import Subtask


def recalculate_subtask_files_count(subtask: Subtask):
    from api.services.subtask_entity_service import SubtaskEntityService

    SubtaskEntityService().recalculate_subtask_files_count(subtask)


def recalculate_subtask_closed_files_count(subtask: Subtask):
    from api.services.subtask_entity_service import SubtaskEntityService

    SubtaskEntityService().recalculate_subtask_closed_files_count(subtask)
