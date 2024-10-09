from api.models import QualityIssueUpdate


def send_quality_issue_created_email_notification(quality_issue_update: QualityIssueUpdate) -> None:
    from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService

    QualityIssueUpdateEntityService().send_email_about_created_quality_issue(quality_issue_update)


def send_email_notification_about_changed_quality_issue_status(quality_issue_update: QualityIssueUpdate) -> None:
    from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService

    QualityIssueUpdateEntityService().send_email_about_update(quality_issue_update)


def send_email_notification_about_created_quality_issue_comment(quality_issue_update: QualityIssueUpdate) -> None:
    from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService

    QualityIssueUpdateEntityService().send_email_about_update(quality_issue_update)
