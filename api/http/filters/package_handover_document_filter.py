from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import Package, PackageActivity, PackageHandoverDocumentType, PackageHandoverDocumentGroup, \
    PackageHandoverDocumentMedia, PackageHandoverDocument, Project, Company


class PackageHandoverDocumentFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('package_activity__name', 'package_activity_name',),
        ),
    )

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover__company',
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_company'
    )

    def filter_by_company(self, queryset, name, value):
        if value:
            return queryset.filter(
                packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__company__in=value,
                packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__company__deleted__isnull=True,
                packagehandoverdocumentmedia__packagehandoverdocumentmediaupdate__deleted__isnull=True,
                packagehandoverdocumentmedia__deleted__isnull=True,
            )
        return queryset

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover__package_matrix__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package'
    )

    def filter_by_package(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_matrix(queryset, name, value)

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget,
    )

    project = rest_framework.ModelMultipleChoiceFilter(
        field_name='project',
        queryset=Project.objects.all(),
        widget=QueryArrayWidget,
    )

    document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document_type',
        queryset=PackageHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
    )

    document_group = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document_type__group',
        queryset=PackageHandoverDocumentGroup.objects.all(),
        widget=QueryArrayWidget,
    )

    status = rest_framework.MultipleChoiceFilter(
        field_name='packagehandoverdocumentmedia__status',
        widget=QueryArrayWidget,
        choices=PackageHandoverDocumentMedia.Status.choices,
        method='filter_by_status'
    )

    def filter_by_status(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, packagehandoverdocumentmedia__deleted__isnull=True).distinct()
        return queryset

    def __filter_by_not_deleted_package_matrix(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value},
                                   package_handover__deleted__isnull=True,
                                   package_handover__package_matrix__deleted__isnull=True).distinct()
        return queryset

    class Meta:
        model = PackageHandoverDocument
        fields = ('package_handover', 'package_handover_document_type',)
