from django.template.defaultfilters import register


@register.filter('color_task_status')
def color_task_status(value):
    if value == 'accepted':
        color = '#01B140'
    elif value == 'part_complete':
        color = '#00A2E0'
    elif value == 'rejected':
        color = '#FFD100'
    elif value == 'not_verified':
        color = '#999999'
    elif value == 'not_applicable':
        color = '#999999'
    elif value == 'outstanding':
        color = '#FF0F19'
    else:
        color = '#000000'

    return color
