from collections import OrderedDict
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi


def base_response_empty_scheme(description: str = '', is_response_204: bool = False) -> openapi.Response:
    if is_response_204:
        description = description or _('This should not crash (response object with no schema)')
        return openapi.Response(description=description)
    description = description or _('An empty object returns.')
    return openapi.Response(description, openapi.Schema(type=openapi.TYPE_OBJECT, description=_('An empty object')))


def errors_response_scheme(description: str) -> openapi.Response:
    return openapi.Response(description, openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ('detail', openapi.Schema(type=openapi.TYPE_STRING, description=_('Error Information'))),
            ('code', openapi.Schema(type=openapi.TYPE_STRING, description=_('Error Code'))),
        )),
        required=['detail']
    ))
