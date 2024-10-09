from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import AssetHandover, LocationMatrix, PackageActivity, Package, Company

AssetHandover.objects.filter()
class AssetHandoverFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('package_activity', 'package_activity',),
            ('location_matrix', 'location_matrix',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('id', 'id',),
        ),
    )

    building = CharInFilter(field_name='location_matrix__building', widget=QueryArrayWidget)
    area = CharInFilter(field_name='location_matrix__area', widget=QueryArrayWidget)
    level = CharInFilter(field_name='location_matrix__level', widget=QueryArrayWidget)

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_matrix_company',
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_company'
    )

    def filter_by_company(self, queryset, name, value):
        if value:
            return queryset.filter(
                assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__in=value,
                assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__deleted__isnull=True,
                assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__deleted__isnull=True,
                assethandoverdocument__assethandoverdocumentmedia__deleted__isnull=True,
            )
        return queryset

    location_matrix = rest_framework.ModelMultipleChoiceFilter(
        queryset=LocationMatrix.objects.all(),
        field_name='location_matrix',
        widget=QueryArrayWidget,
        method='filter_by_location_matrix'
    )

    def filter_by_location_matrix(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, location_matrix__deleted__isnull=True).distinct()
        return queryset

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        queryset=PackageActivity.objects.all(),
        field_name='package_activity',
        widget=QueryArrayWidget,
        method='filter_by_package_activity'
    )

    def filter_by_package_activity(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, package_activity__deleted__isnull=True).distinct()
        return queryset

    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        field_name='package',
        widget=QueryArrayWidget,
        method='filter_by_package'
    )

    def filter_by_package(self, queryset, name, value):
        if value:
            return queryset.filter(
                package_activity__packagematrix__deleted__isnull=True,
                package_activity__packagematrix__package__in=value,
                package_activity__packagematrix__project_id=self.request.parser_context['kwargs']['project_pk'],
            ).distinct()
        return queryset

    class Meta:
        model = AssetHandover
        fields = ('package_activity', 'location_matrix',)
