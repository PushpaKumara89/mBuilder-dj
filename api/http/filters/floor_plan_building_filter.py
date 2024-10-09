from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import FloorPlan, Package


class FloorPlanBuildingFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('package', 'package',),
            ('building', 'building',),
        ),
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget
    )

    building = CharInFilter(field_name='building', widget=QueryArrayWidget)

    class Meta:
        model = FloorPlan
        fields = ('building', 'package', 'sort',)
