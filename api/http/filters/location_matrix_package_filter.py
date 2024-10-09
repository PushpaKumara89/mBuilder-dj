from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import LocationMatrixPackage, Package


class LocationMatrixPackageFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('location_matrix', 'location_matrix'),
            ('package_matrix', 'package_matrix'),
        ),
    )

    package = rest_framework.ModelChoiceFilter(queryset=Package.objects.all(), field_name='package_matrix__package')
    building = CharInFilter(field_name='location_matrix__building', widget=QueryArrayWidget)
    level = CharInFilter(field_name='location_matrix__level', widget=QueryArrayWidget)
    area = CharInFilter(field_name='location_matrix__area', widget=QueryArrayWidget)

    class Meta:
        model = LocationMatrixPackage
        fields = ('location_matrix', 'package_matrix',)
