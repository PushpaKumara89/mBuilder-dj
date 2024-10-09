from django.template.defaultfilters import register

from api.models import QualityIssue


@register.filter('is_show_quality_issue_action_required_by')
def is_show_quality_issue_action_required_by(quality_issue: dict):
    return quality_issue['status'] != QualityIssue.Status.CLOSED.value and quality_issue['status'] != QualityIssue.Status.REMOVED.value
