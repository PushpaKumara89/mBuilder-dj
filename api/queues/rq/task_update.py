from django_rq import job

from api.queues.core.task_update import \
    send_task_status_changed_email_notification as send_task_status_changed_email_notification_core


@job('default')
def send_task_status_changed_email_notification(task_update):
    send_task_status_changed_email_notification_core(task_update)
