from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.http.filters.subtask import SubtaskOrderingFilter
from api.models import Subtask, Package, PackageActivity, PackageActivityTask, User, QualityIssue, Company


class SubtaskFilter(rest_framework.FilterSet):
    sort = SubtaskOrderingFilter(
        fields=(
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('files_count', 'files_count',),
            ('description', 'description',),
            ('location_description', 'location_description',),
            ('id', 'id',),
            ('is_defect', 'is_defect',),
            ('status', 'status',),
            ('task__location_matrix__area', 'area',),
            ('task__location_matrix__building', 'building',),
            ('task__location_matrix__level', 'level',),
            ('task__package_activity__name', 'package_activity',),
            ('task__package_activity__packagematrix__package', 'package',),
            ('task__package_activity_task__description', 'package_activity_task',),
            ('user__last_name', 'user',),
            ('company__name', 'subcontractor',),
            ('due_date', 'due_date',),
        ),
    )

    building = CharInFilter(
        field_name='task__location_matrix__building',
        widget=QueryArrayWidget
    )
    level = CharInFilter(
        field_name='task__location_matrix__level',
        widget=QueryArrayWidget
    )
    area = CharInFilter(
        field_name='task__location_matrix__area',
        widget=QueryArrayWidget
    )
    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package'
    )
    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='task__package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget
    )
    package_activity_task = rest_framework.ModelMultipleChoiceFilter(
        field_name='task__package_activity_task',
        queryset=PackageActivityTask.objects.all(),
        widget=QueryArrayWidget
    )
    user = rest_framework.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        widget=QueryArrayWidget
    )
    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=Subtask.Status.choices,
        widget=QueryArrayWidget
    )
    except_status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=Subtask.Status.choices,
        widget=QueryArrayWidget,
        exclude=True
    )

    quality_issue = rest_framework.ModelMultipleChoiceFilter(
        field_name='quality_issue',
        queryset=QualityIssue.objects.all(),
        widget=QueryArrayWidget
    )

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='company',
        queryset=Company.objects.all(),
        widget=QueryArrayWidget
    )

    created_at__gte = rest_framework.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_at__lte = rest_framework.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    updated_at__gte = rest_framework.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte'
    )
    updated_at__lte = rest_framework.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte'
    )

    def filter_by_package(self, queryset, name, value):
        if len(value) == 0:
            return queryset

        filters = {
            'task__package_activity__packagematrix__package__in': [package.pk for package in value],
            'task__package_activity__packagematrix__deleted__isnull': True
        }

        if 'project_pk' in self.request.parser_context['kwargs']:
            filters['task__package_activity__packagematrix__project'] = self.request.parser_context['kwargs']['project_pk']

        return queryset.filter(**filters)

    class Meta:
        model = Subtask
        fields = ('task', 'created_at', 'updated_at', 'is_defect',)
