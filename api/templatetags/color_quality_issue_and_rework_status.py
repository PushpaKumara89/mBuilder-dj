from django.template.defaultfilters import register

from api.models import QualityIssue, Subtask


@register.filter('color_quality_issue_and_rework_status')
def color_quality_issue_and_rework_status(value):
    if value in [QualityIssue.Status.UNDER_REVIEW.value, QualityIssue.Status.REMOVED.value, Subtask.Status.REMOVED]:
        return '#999999'
    elif value in [QualityIssue.Status.CONTESTED.value, Subtask.Status.CONTESTED.value]:
        return '#00A2E0'
    elif value in [QualityIssue.Status.IN_PROGRESS.value, QualityIssue.Status.INSPECTION_REJECTED.value, Subtask.Status.IN_PROGRESS.value]:
        return '#FFD100'
    elif value in [QualityIssue.Status.DECLINED.value, Subtask.Status.DECLINED.value]:
        return '#FF9000'
    elif value in [QualityIssue.Status.UNDER_INSPECTION.value, Subtask.Status.UNDER_INSPECTION.value]:
        return '#FF6800'
    elif value in [QualityIssue.Status.REQUESTING_APPROVAL.value, Subtask.Status.REQUESTING_APPROVAL.value]:
        return '#AF52DE'
    elif value in [QualityIssue.Status.REQUESTED_APPROVAL_REJECTED.value, Subtask.Status.REQUESTED_APPROVAL_REJECTED.value]:
        return '#FF3B30'
    elif value in [QualityIssue.Status.CLOSED.value, Subtask.Status.CLOSED.value]:
        return '#01B140'
    else:
        return '#000000'
