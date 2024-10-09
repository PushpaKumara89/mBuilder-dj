from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.non_validating_multiple_choice_filter import NonValidatingMultipleChoiceFilter
from api.models import Package, PackageActivity, LocationMatrix, AssetHandoverDocumentMedia, AssetHandoverDocumentType


class AssetHandoverCompanyFilterKwargs(rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filter_kwargs = {}

    level = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover__location_matrix__level',
        widget=QueryArrayWidget,
        method='filter_by_level'
    )

    def filter_by_level(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__level__in=value
            )
        return queryset

    area = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover__location_matrix__area',
        widget=QueryArrayWidget,
        method='filter_by_area'
    )

    def filter_by_area(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__area__in=value
            )
        return queryset

    building = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover__location_matrix__building',
        widget=QueryArrayWidget,
        method='filter_by_building'
    )

    def filter_by_building(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__building__in=value
            )
        return queryset

    location_matrix = rest_framework.ModelMultipleChoiceFilter(
        queryset=LocationMatrix.objects.all(),
        field_name='asset_handover__location_matrix',
        widget=QueryArrayWidget,
        method='filter_by_location_matrix'
    )

    def filter_by_location_matrix(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__in=value
            )
        return queryset

    document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='document_type',
        queryset=AssetHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_document_type'
    )

    def filter_by_document_type(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__document_type__in=value,
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__deleted__isnull=True,
            )
        return queryset

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        widget=QueryArrayWidget,
        choices=AssetHandoverDocumentMedia.Status.choices,
        method='filter_by_status'
    )

    def filter_by_status(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__status__in=value
            )
        return queryset

    package = rest_framework.ModelMultipleChoiceFilter(
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        field_name='package',
        method='filter_by_package'
    )

    def filter_by_package(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__package__in=value,
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__enabled=True,
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__deleted__isnull=True
            )
        return queryset

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget,
        field_name='package_activity',
        method='filter_by_package_activity'
    )

    def filter_by_package_activity(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__package_activity__in=value,
                assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__deleted__isnull=True
            )
        return queryset

    def get_filter_kwargs(self):
        if self.is_valid():
            self.filter_queryset(self.queryset.all())
        return self._filter_kwargs

    class Meta:
        fields = ('asset_handover__location_matrix__level', 'asset_handover__location_matrix__area', 'asset_handover__location_matrix__building',
                  'asset_handover__location_matrix', 'document_type', 'status', 'package', 'package_activity')
