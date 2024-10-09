from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import PackageActivity, Package


class PackageMatrixActivityFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'create_at'),
        ),
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='packagematrix__package',
        queryset=Package.all_objects.all(),
        widget=QueryArrayWidget
    )

    class Meta:
        model = PackageActivity
        fields = ('name', 'created_at',)
