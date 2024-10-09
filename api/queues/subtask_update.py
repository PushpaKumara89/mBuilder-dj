from typing import List

from api.queues.core.base import use_rq_if_configured

from api.queues.rq.subtask_update import \
    delete_on_location_matrix_delete as delete_on_location_matrix_delete_rq, \
    send_email_notification_about_created_subtask as send_email_notification_about_created_subtask_rq, \
    send_email_notification_about_changed_subtask_status as send_email_notification_about_changed_subtask_status_rq, \
    send_email_notification_about_created_comment as send_email_notification_about_created_comment_rq

from api.queues.celery.subtask_update import \
    delete_on_location_matrix_delete as delete_on_location_matrix_delete_celery, \
    send_email_notification_about_created_subtask as send_email_notification_about_created_subtask_celery, \
    send_email_notification_about_changed_subtask_status as send_email_notification_about_changed_subtask_status_celery, \
    send_email_notification_about_created_comment as send_email_notification_about_created_comment_celery

from api.models import SubtaskUpdate


@use_rq_if_configured(delete_on_location_matrix_delete_rq)
def delete_on_location_matrix_delete(location_matrices_ids: List[int], context) -> None:
    delete_on_location_matrix_delete_celery.delay(location_matrices_ids, context)


@use_rq_if_configured(send_email_notification_about_created_subtask_rq)
def send_email_notification_about_created_subtask(subtask_update):
    send_email_notification_about_created_subtask_celery.delay(subtask_update)


@use_rq_if_configured(send_email_notification_about_changed_subtask_status_rq)
def send_email_notification_about_changed_subtask_status(subtask_update: SubtaskUpdate):
    send_email_notification_about_changed_subtask_status_celery.delay(subtask_update)


@use_rq_if_configured(send_email_notification_about_created_comment_rq)
def send_email_notification_about_created_comment(subtask_update: SubtaskUpdate):
    send_email_notification_about_created_comment_celery.delay(subtask_update)
