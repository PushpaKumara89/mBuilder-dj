from mbuild.settings import app as celery_app

from api.queues.core.subtasks import recalculate_subtask_files_count as recalculate_subtask_files_count_core, \
    recalculate_subtask_closed_files_count as recalculate_subtask_closed_files_count_core

from api.models.subtask import Subtask


@celery_app.task(queue='default', time_limit=3600)
def recalculate_subtask_files_count(subtask: Subtask):
    recalculate_subtask_files_count_core(subtask)


@celery_app.task(queue='default', time_limit=3600)
def recalculate_subtask_closed_files_count(subtask: Subtask):
    recalculate_subtask_closed_files_count_core(subtask)
