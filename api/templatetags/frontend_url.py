from django.conf import settings
from django.template.defaultfilters import register


@register.simple_tag
def frontend_url():
    return settings.FRONTEND_URL
