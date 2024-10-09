from datetime import datetime

from django.template.defaultfilters import register

from api.utilities.time_utilities import change_timezone_to_london


@register.filter('format_to_local_london_date')
def format_to_local_london_date(date: datetime):
    created_at_date = change_timezone_to_london(date)

    return created_at_date.strftime('%d %b, %Y') + '\n' + created_at_date.strftime('%I:%M%p')
