from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.number_in_filter import NumberInFilter
from api.models import Company, Package, PackageActivity


class HandoverDocumentCompanyFilter(rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filter_kwargs = {}

    def get_filter_kwargs(self):
        return self._filter_kwargs

    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name',),
            ('created_at', 'created_at',),
        ),
    )

    id = NumberInFilter(
        field_name='id',
        widget=QueryArrayWidget
    )

    name = rest_framework.CharFilter(field_name='name', lookup_expr='iexact')
    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        field_name='handoverdocument__package',
        method='filter_by_multiple_value'
    )

    def filter_by_package(self, queryset, field_name, value):
        if value:
            self._filter_kwargs[f'{field_name}__in'] = value
        return queryset

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        queryset=PackageActivity.objects.all(),
        field_name='handoverdocument__package_activity',
        method='filter_by_multiple_value'
    )

    def filter_by_multiple_value(self, queryset, field_name, value):
        if value:
            self._filter_kwargs[f'{field_name}__in'] = value
        return queryset

    class Meta:
        model = Company
        fields = ('name',)
