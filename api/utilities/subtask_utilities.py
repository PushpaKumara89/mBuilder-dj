from django.db.models import BooleanField, IntegerField, Q
from django.db.models.expressions import RawSQL, Case, When, Value

from api.models import Subtask
from api.models.queryset.utilites.make_expressions import numerate_when_expressions
from api.utilities.location_matrix_utilities import annotate_location_matrix_level_parts


def apply_common_filters_queryset(queryset, request, kwargs, filter_subcontractors=True):
    if request.query_params.get('all_with_activity'):
        queryset = Subtask.all_objects.all()

    sort_fields = request.query_params.getlist('sort')

    if 'default_sort' in sort_fields:
        queryset = order_by_status(queryset, request)

    if 'project_pk' in kwargs:
        filters = {
            'task__project': kwargs['project_pk']
        }

        if filter_subcontractors and bool(request.user) and request.user.is_subcontractor:
            filters['company'] = request.user.company

        return queryset.filter(**filters)

    return queryset


def apply_default_ordering(queryset, request):
    if 'sort' not in request.query_params:
        queryset = queryset.\
            annotate(closed=RawSQL('"subtasks"."status" = %s',
                                   (Subtask.Status.CLOSED,),
                                   output_field=BooleanField())). \
            order_by('closed',
                     'building',
                     RawSQL('subtasks.level_number', ()).desc(),
                     RawSQL('subtasks.level_postfix', ()),
                     'area',
                     'task__package_activity').all()

    return queryset


def order_by_status(queryset, request):
    user = request.user
    order_by_fields = ['building', RawSQL('subtasks.level_number', ()).desc(), RawSQL('subtasks.level_postfix', ()), 'subtasks.area', 'id']

    if getattr(user, 'is_staff', False):
        order_by_fields.insert(0, RawSQL('status_weight_for_staff', ()))
    elif getattr(user, 'is_subcontractor', False):
        order_by_fields.insert(0, RawSQL('status_weight_for_subcontractor', ()))

    return queryset.order_by(*order_by_fields)
