from django.contrib.contenttypes.models import ContentType
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import FloorPlan
from api.models.floor_plan_revision import FloorPlanRevision


class FloorPlanRevisionFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('date_created', 'created_at'),
            ('id', 'id'),
        ),
    )

    floor_plan = CharInFilter(
        field_name='version__object_id',
        method='filter_by_floor_plan',
        widget=QueryArrayWidget
    )

    def filter_by_floor_plan(self, queryset, field_name, value):
        if value:
            floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
            return queryset.filter(
                version__content_type=floor_plan_content_type,
                **{f'{field_name}__in': value}
            )

        return queryset

    class Meta:
        model = FloorPlanRevision
        fields = ('id', 'user', 'comment',)
