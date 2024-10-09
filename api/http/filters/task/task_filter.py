from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.http.filters.task.task_order_filter import TaskOrderFilter
from api.models import Task, Package, PackageActivity, PackageActivityTask, User


class TaskFilter(rest_framework.FilterSet):
    sort = TaskOrderFilter(
        fields=(
            ('building', 'building',),
            ('level', 'level',),
            ('area', 'area',),
            ('package', 'package',),
            ('package_activity__name', 'package_activity',),
            ('package_activity_task__description', 'package_activity_task',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('user__last_name', 'user',),
            ('status', 'status',),
            ('id', 'id',),
        ),
    )

    building = CharInFilter(widget=QueryArrayWidget)
    level = CharInFilter(widget=QueryArrayWidget)
    area = CharInFilter(widget=QueryArrayWidget)
    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        distinct=False
    )

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget
    )
    package_activity_task = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_activity_task',
        queryset=PackageActivityTask.objects.all(),
        widget=QueryArrayWidget
    )
    user = rest_framework.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_user'
    )

    def filter_by_user(self, queryset, field_name, value):
        if value and not (self.request.user.is_client or self.request.user.is_consultant):
            queryset = queryset.filter(**{f'{field_name}__in': value})

        return queryset

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=Task.Statuses.choices,
        widget=QueryArrayWidget,
        distinct=False
    )
    exclude_status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=Task.Statuses.choices,
        widget=QueryArrayWidget,
        exclude=True,
        distinct=False
    )
    is_default_for_subtask = rest_framework.BooleanFilter(
        field_name='package_activity_task__is_default_for_subtask'
    )
    created_at__gte = rest_framework.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        method='filter_by_created_at__gte'
    )

    def filter_by_created_at__gte(self, queryset, field_name, value):
        if value and not (self.request.user.is_client or self.request.user.is_consultant):
            queryset = queryset.filter(**{f'{field_name}__gte': value})

        return queryset

    created_at__lte = rest_framework.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        method='filter_by_created_at__lte'
    )

    def filter_by_created_at__lte(self, queryset, field_name, value):
        if value and not (self.request.user.is_client or self.request.user.is_consultant):
            queryset = queryset.filter(**{f'{field_name}__lte': value})

        return queryset

    updated_at__gte = rest_framework.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte'
    )
    updated_at__lte = rest_framework.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Task
        fields = (
            'location_matrix', 'package_activity', 'package_activity_task',
            'created_at', 'updated_at', 'user', 'status'
        )
