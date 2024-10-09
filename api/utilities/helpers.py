from distutils import util
from typing import Union, Any

from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class Request(object):
    # Framework cannot serialize all request object. Get only needed for work items.
    def __init__(self, user, query_params):
        self.user = user
        self.query_params = query_params if type(query_params) is MultiValueDict else MultiValueDict(query_params)


def get_array_parameter(parameter_name, query_params):
    empty_values = ('', None, 'null', 'undefined')
    parameter_values = query_params.getlist(parameter_name, query_params.getlist(parameter_name + '[]'))
    return [parameter_value for parameter_value in parameter_values if parameter_value not in empty_values]


def get_int_array_parameter(parameter_name, query_params):
    parameter_values = get_array_parameter(parameter_name, query_params)
    return [int(value) for value in parameter_values if str(value).isdigit()]


def get_unique_objects_from_list(data, field='id'):
    return list({el[field] if el is list else getattr(el, field): el for el in data}.values())


def is_expanded(request, key):
    if expand := get_array_parameter('expand', request.query_params):
        return key in expand

    return False


def get_boolean_query_param(query_params: Union[dict, MultiValueDict], param_name: str, default: bool = None):
    try:
        return util.strtobool(query_params.get(param_name)) if param_name in query_params else default
    except ValueError:
        raise ValidationError({param_name: 'Parameter should be a boolean.'})


def get_to_email_status_name(cls: Any, status: str) -> str:
    assert hasattr(cls, 'Status')
    if status == cls.Status.DECLINED:
        return _('Subcontractor Declined')
    return dict(cls.Status.choices)[status]
