from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import LocationMatrix


class LocationsFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('building', 'building'),
            ('level', 'level'),
            ('area', 'area'),
        ),
    )

    building = CharInFilter(field_name='building', widget=QueryArrayWidget)
    level = CharInFilter(field_name='level', widget=QueryArrayWidget)
    area = CharInFilter(field_name='area', widget=QueryArrayWidget)

    class Meta:
        model = LocationMatrix
        fields = ('building', 'level', 'area',)
