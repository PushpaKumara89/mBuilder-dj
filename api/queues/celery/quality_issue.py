from mbuild.settings import app as celery_app

from api.queues.core.quality_issue import \
    send_quality_issue_created_email_notification as send_quality_issue_created_email_notification_core, \
    send_email_notification_about_changed_quality_issue_status as send_email_notification_about_changed_quality_issue_status_core, \
    send_email_notification_about_created_quality_issue_comment as send_email_notification_about_created_quality_issue_comment_core

from api.models import QualityIssueUpdate


@celery_app.task(queue='default')
def send_quality_issue_created_email_notification(quality_issue_update: QualityIssueUpdate) -> None:
    send_quality_issue_created_email_notification_core(quality_issue_update)


@celery_app.task(queue='default')
def send_email_notification_about_changed_quality_issue_status(quality_issue_update: QualityIssueUpdate) -> None:
    send_email_notification_about_changed_quality_issue_status_core(quality_issue_update)


@celery_app.task(queue='default')
def send_email_notification_about_created_quality_issue_comment(quality_issue_update: QualityIssueUpdate) -> None:
    send_email_notification_about_created_quality_issue_comment_core(quality_issue_update)
