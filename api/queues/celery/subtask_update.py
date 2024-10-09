from typing import List

from mbuild.settings import app as celery_app

from api.queues.core.subtask_update import \
    delete_on_location_matrix_delete as delete_on_location_matrix_delete_core, \
    send_email_notification_about_created_subtask as send_email_notification_about_created_subtask_core, \
    send_email_notification_about_changed_subtask_status as send_email_notification_about_changed_subtask_status_core, \
    send_email_notification_about_created_comment as send_email_notification_about_created_comment_core

from api.models import SubtaskUpdate


@celery_app.task(queue='default', time_limit=3600)
def delete_on_location_matrix_delete(location_matrices_ids: List[int], context) -> None:
    delete_on_location_matrix_delete_core(location_matrices_ids, context)


@celery_app.task(queue='default', time_limit=3600)
def send_email_notification_about_created_subtask(subtask_update):
    send_email_notification_about_created_subtask_core(subtask_update)


@celery_app.task(queue='default')
def send_email_notification_about_changed_subtask_status(subtask_update: SubtaskUpdate):
    send_email_notification_about_changed_subtask_status_core(subtask_update)


@celery_app.task(queue='default')
def send_email_notification_about_created_comment(subtask_update: SubtaskUpdate):
    send_email_notification_about_created_comment_core(subtask_update)
