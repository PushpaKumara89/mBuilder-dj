from api.queues.core.base import use_rq_if_configured

from api.queues.rq.task_update import \
    send_task_status_changed_email_notification as send_task_status_changed_email_notification_rq
from api.queues.celery.task_update import \
    send_task_status_changed_email_notification as send_task_status_changed_email_notification_celery


@use_rq_if_configured(send_task_status_changed_email_notification_rq)
def send_task_status_changed_email_notification(task_update):
    send_task_status_changed_email_notification_celery.delay(task_update)
