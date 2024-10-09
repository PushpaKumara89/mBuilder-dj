from django.template.defaultfilters import register

from api.models import Subtask


@register.filter('is_show_action_required_by')
def is_show_action_required_by(subtask: dict):
    return subtask['status'] != Subtask.Status.CLOSED.value and subtask['status'] != Subtask.Status.REMOVED.value
