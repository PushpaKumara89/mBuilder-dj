from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import Company, PackageActivity, HandoverDocument, Package


class HandoverDocumentFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name',),
            ('created_at', 'created_at',),
        ),
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        widget=QueryArrayWidget
    )
    package_activity = rest_framework.ModelMultipleChoiceFilter(
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget
    )
    company = rest_framework.ModelMultipleChoiceFilter(
        queryset=Company.objects.all(),
        widget=QueryArrayWidget
    )

    class Meta:
        model = HandoverDocument
        fields = ('package', 'package_activity', 'company',)
