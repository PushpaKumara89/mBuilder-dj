from django_rq import job

from api.queues.core.subtasks import recalculate_subtask_files_count as recalculate_subtask_files_count_core, \
    recalculate_subtask_closed_files_count as recalculate_subtask_closed_files_count_core

from api.models import Subtask


@job('default', timeout=3600)
def recalculate_subtask_files_count(subtask: Subtask):
    recalculate_subtask_files_count_core(subtask)


@job('default', timeout=3600)
def recalculate_subtask_closed_files_count(subtask: Subtask):
    recalculate_subtask_closed_files_count_core(subtask)
