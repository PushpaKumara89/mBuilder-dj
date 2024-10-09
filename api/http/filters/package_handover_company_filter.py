from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import PackageHandoverDocumentGroup, PackageHandoverDocumentMedia, PackageHandoverDocumentType, Package, PackageActivity


class PackageHandoverCompanyFilterKwargs(rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filter_kwargs = {}

    document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='document_type',
        queryset=PackageHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_document_type'
    )

    def filter_by_document_type(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_handover_document_type__in=value,
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__deleted__isnull=True,
            )
        return queryset

    document_group = rest_framework.ModelMultipleChoiceFilter(
        field_name='document_group',
        queryset=PackageHandoverDocumentGroup.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_document_group'
    )

    def filter_by_document_group(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_handover_document_type__group__in=value,
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__deleted__isnull=True,
            )
        return queryset

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        widget=QueryArrayWidget,
        choices=PackageHandoverDocumentMedia.Status.choices,
        method='filter_by_status'
    )

    def filter_by_status(self, queryset, name, value):
        if value:
            self._filter_kwargs.update(
                packagehandoverdocumentmediaupdate__package_handover_document_media__status__in=value
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
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_handover__package_matrix__package__in=value,
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_handover__package_matrix__deleted__isnull=True,
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_handover__deleted__isnull=True
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
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__package_activity__in=value,
                packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__deleted__isnull=True,
                packagehandoverdocumentmediaupdate__package_handover_document_media__deleted__isnull=True
            )
        return queryset

    def get_filter_kwargs(self):
        if self.is_valid():
            self.filter_queryset(self.queryset.all())
        return self._filter_kwargs

    class Meta:
        fields = ('document_type', 'document_group', 'status', 'package', 'package_activity',)
