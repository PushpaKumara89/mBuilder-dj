from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import FloorPlanArea, FloorPlan, Package


class FloorPlanAreaFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('plan', 'plan',),
            ('area', 'area',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )

    floor_plan = rest_framework.ModelMultipleChoiceFilter(
        field_name='floor_plan',
        queryset=FloorPlan.objects.all(),
        widget=QueryArrayWidget
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='floor_plan__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget
    )

    building = CharInFilter(
        field_name='floor_plan__building',
        widget=QueryArrayWidget
    )
    level = CharInFilter(
        field_name='floor_plan__level',
        widget=QueryArrayWidget
    )
    area = CharInFilter(widget=QueryArrayWidget)

    class Meta:
        model = FloorPlanArea
        fields = ('floor_plan', 'area',)
