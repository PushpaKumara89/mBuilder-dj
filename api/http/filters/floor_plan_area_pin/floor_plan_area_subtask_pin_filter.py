from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import FloorPlanArea, FloorPlanAreaPin, FloorPlan


class FloorPlanAreaSubtaskPinFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('object_id', 'object_id',),
            ('floor_plan_area', 'floor_plan_area',),
            ('created_at', 'created_at',),
        ),
    )

    object_id = rest_framework.NumberFilter()
    floor_plan_area = rest_framework.ModelMultipleChoiceFilter(
        queryset=FloorPlanArea.objects.all()
    )
    floor_plan = rest_framework.ModelMultipleChoiceFilter(
        field_name='floor_plan_area__floor_plan',
        queryset=FloorPlan.objects.all()
    )
    building = CharInFilter(
        field_name='floor_plan_area__floor_plan__building',
        widget=QueryArrayWidget
    )
    level = CharInFilter(
        field_name='floor_plan_area__floor_plan__level',
        widget=QueryArrayWidget
    )
    area = CharInFilter(
        field_name='floor_plan_area__area',
        widget=QueryArrayWidget
    )

    class Meta:
        model = FloorPlanAreaPin
        fields = ('object_id', 'floor_plan_area')
