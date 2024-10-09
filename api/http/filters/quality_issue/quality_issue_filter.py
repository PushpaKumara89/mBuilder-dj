from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.http.filters.quality_issue.quality_issue_ordering_filter import QualityIssueOrderingFilter
from api.models import QualityIssue, User, Package, PackageActivity


class QualityIssueFilter(rest_framework.FilterSet):
    sort = QualityIssueOrderingFilter(
        fields=(
            ('id', 'id',),
            ('status', 'status',),
            ('user', 'created_by',),
            ('due_date', 'due_date',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('description', 'description',),
            ('location_matrix__area', 'area',),
            ('location_matrix__level', 'level',),
            ('location_matrix__building', 'building',),
            ('response_category__name', 'response_category',),
        ),
    )

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=QualityIssue.Status.choices,
        widget=QueryArrayWidget
    )

    except_status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=QualityIssue.Status.choices,
        widget=QueryArrayWidget,
        exclude=True
    )

    building = CharInFilter(
        field_name='location_matrix__building',
        widget=QueryArrayWidget
    )
    level = CharInFilter(
        field_name='location_matrix__level',
        widget=QueryArrayWidget
    )
    area = CharInFilter(
        field_name='location_matrix__area',
        widget=QueryArrayWidget
    )
    user = rest_framework.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        widget=QueryArrayWidget
    )
    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='location_matrix__locationmatrixpackage__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget
    )
    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='location_matrix__locationmatrixpackage__package_activity',
        queryset=PackageActivity.objects.all(),
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
    subtask_is_defect = rest_framework.BooleanFilter(
        field_name='subtask__is_defect'
    )

    class Meta:
        model = QualityIssue
        fields = ('status',)
