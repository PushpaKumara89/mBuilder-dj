from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import LocationMatrix


class LocationMatrixFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('building', 'building'),
            ('level', 'level'),
            ('area', 'area'),
        ),
    )
    has_published_tasks = rest_framework.BooleanFilter(field_name='locationmatrixpackage__enabled')
    building = CharInFilter(field_name='building', widget=QueryArrayWidget)
    area = CharInFilter(field_name='area', widget=QueryArrayWidget)
    level = CharInFilter(field_name='level', widget=QueryArrayWidget)

    class Meta:
        model = LocationMatrix
        fields = ('building', 'level', 'area',)
