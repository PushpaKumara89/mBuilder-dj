from django.template.defaultfilters import register


@register.filter('format_report_entity_output')
def format_report_entity_output(value):
    output_name = value
    if value == 'Task':
        output_name = 'Quality Report'
    elif value == 'Subtask':
        output_name = 'Rework and Defects'
    elif value == 'Handover Document':
        output_name = 'Handover Information Report'

    return output_name
