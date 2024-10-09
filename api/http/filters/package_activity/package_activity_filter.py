from django.db.models import Exists, OuterRef
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.utilities.helpers import get_int_array_parameter
from .package_activity_ordering_filter import PackageActivityOrderingFilter
from api.models import PackageActivity, Project, PackageMatrix, Company
from ..base_filters.number_in_filter import NumberInFilter


class PackageActivityFilter(rest_framework.FilterSet):
    sort = PackageActivityOrderingFilter(
        fields=(
            ('name', 'name'),
        ),
    )

    id = NumberInFilter(
        field_name='id',
        widget=QueryArrayWidget
    )

    asset_handover_document_company = rest_framework.ModelMultipleChoiceFilter(
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_asset_handover_document_company'
    )

    def filter_by_asset_handover_document_company(self, queryset, name, value):
        if value:
            project_filter = get_int_array_parameter('project', self.request.query_params)
            filter_kwargs = {}
            if project_filter:
                filter_kwargs.update(assethandover__project__in=project_filter)
            return queryset.filter(
                assethandover__assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__in=value,
                assethandover__assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__deleted__isnull=True,
                assethandover__assethandoverdocument__assethandoverdocumentmedia__assethandoverdocumentmediaupdate__deleted__isnull=True,
                assethandover__assethandoverdocument__assethandoverdocumentmedia__deleted__isnull=True,
                assethandover__assethandoverdocument__deleted__isnull=True,
                **filter_kwargs,
            )
        return queryset

    exclude_bound_with_project = rest_framework.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        method='exclude_for_project'
    )

    def exclude_for_project(self, queryset, name, value):
        if len(value) > 0:
            return queryset.exclude(
                Exists(PackageMatrix.objects.filter(
                    package_activity__pk=OuterRef('pk'),
                    deleted__isnull=True,
                    project=value[0])
                ))

        return queryset

    package_handover_document_company = rest_framework.ModelMultipleChoiceFilter(
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_handover_document_company'
    )

    def filter_by_package_handover_document_company(self, queryset, name, value):
        if value:
            project_filter = get_int_array_parameter('project', self.request.query_params)
            filter_kwargs = {}
            if project_filter:
                filter_kwargs.update(packagehandoverdocument__project__in=project_filter)
            return queryset.filter(
                packagehandoverdocument__packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__company__in=value,
                packagehandoverdocument__packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__company__deleted__isnull=True,
                packagehandoverdocument__packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__deleted__isnull=True,
                packagehandoverdocument__packagehandoverdocumentmedia__deleted__isnull=True,
                packagehandoverdocument__deleted__isnull=True,
                **filter_kwargs,
            )
        return queryset

    class Meta:
        model = PackageActivity
        fields = ('name',)
