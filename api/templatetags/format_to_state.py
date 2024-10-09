from django.forms import model_to_dict
from django.template.defaultfilters import register

from api.utilities.status_flow.subtask_status_change_flow import SubtaskStatusChangeFlow


@register.filter('format_to_state')
def format_subtask_transition_to_state(update, user):
    status_change_flow = SubtaskStatusChangeFlow(model_to_dict(update), user)
    if status_change_flow.is_reopen():
        return 'Reopened'
    elif status_change_flow.is_reject():
        return 'Rejected'
    elif status_change_flow.is_new():
        return 'New'
    return ''
