from django.db.models import Exists, OuterRef
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.http.filters.base_filters.number_in_filter import NumberInFilter
from api.models import FloorPlan, Package, FloorPlanArea


class FloorPlanFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('level', 'level',),
            ('package', 'package',),
            ('building', 'building',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget
    )
    id = NumberInFilter(widget=QueryArrayWidget)
    building = CharInFilter(field_name='building', widget=QueryArrayWidget)
    level = CharInFilter(field_name='level', widget=QueryArrayWidget)
    has_floor_plan_area = rest_framework.BooleanFilter(
        method='filter_by_floor_plan_area_existence'
    )

    def filter_by_floor_plan_area_existence(self, queryset, field_name, value):
        if value is None:
            return queryset

        return queryset.filter(
            Exists(FloorPlanArea.objects.filter(floor_plan=OuterRef('id'), deleted__isnull=True))
        )

    class Meta:
        model = FloorPlan
        fields = ('level', 'building', 'package',)
