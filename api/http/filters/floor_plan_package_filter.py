from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import FloorPlan


class FloorPlanPackageFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('level', 'level',),
            ('package', 'package',),
            ('building', 'building',),
        ),
    )

    building = CharInFilter(field_name='building', widget=QueryArrayWidget, required=True)
    level = CharInFilter(field_name='level', widget=QueryArrayWidget, required=True)

    class Meta:
        model = FloorPlan
        fields = ('level', 'building', 'sort',)
