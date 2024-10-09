from api.queues.core.base import use_rq_if_configured

from api.queues.rq.subtasks import recalculate_subtask_files_count as recalculate_subtask_files_count_rq, \
    recalculate_subtask_closed_files_count as recalculate_subtask_closed_files_count_rq
from api.queues.celery.subtasks import recalculate_subtask_files_count as recalculate_subtask_files_count_celery, \
    recalculate_subtask_closed_files_count as recalculate_subtask_closed_files_count_celery

from api.models.subtask import Subtask


@use_rq_if_configured(recalculate_subtask_files_count_rq)
def recalculate_subtask_files_count(subtask: Subtask):
    recalculate_subtask_files_count_celery.delay(subtask)


@use_rq_if_configured(recalculate_subtask_closed_files_count_rq)
def recalculate_subtask_closed_files_count(subtask: Subtask):
    recalculate_subtask_closed_files_count_celery.delay(subtask)
