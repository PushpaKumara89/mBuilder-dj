from django_filters import rest_framework

from api.models import PackageMatrixCompany


class PackageMatrixCompanyFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('created_at', 'create_at'),
            ('updated_at', 'updated_at'),
            ('package_activity', 'package_activity'),
            ('package_matrix', 'package_matrix'),
        ),
    )

    class Meta:
        model = PackageMatrixCompany
        fields = ('package_matrix', 'company',)
