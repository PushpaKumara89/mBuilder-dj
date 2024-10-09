from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import PackageHandover, Package, PackageActivity, PackageHandoverDocumentType, \
    PackageHandoverDocumentGroup, PackageHandoverDocumentMedia, Company


class PackageHandoverFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
            ('package_matrix__package_activity__name', 'package_activity_name',),
        ),
    )

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_matrix__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package'
    )

    def filter_by_package(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_matrix(queryset, name, value)

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_matrix__company',
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_company'
    )

    def filter_by_company(self, queryset, name, value):
        if value:
            return queryset.filter(
                package_matrix__companies__in=value,
                package_matrix__deleted__isnull=True
            )
        return queryset

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_matrix__package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_activity'
    )

    def filter_by_package_activity(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_matrix(queryset, name, value)

    document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='packagehandoverdocument__package_handover_document_type',
        queryset=PackageHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_document_type'
    )

    def filter_by_document_type(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_handover_document(queryset, name, value)

    document_group = rest_framework.ModelMultipleChoiceFilter(
        field_name='packagehandoverdocument__package_handover_document_type__group',
        queryset=PackageHandoverDocumentGroup.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_document_group'
    )

    def filter_by_document_group(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_handover_document(queryset, name, value)

    status = rest_framework.MultipleChoiceFilter(
        field_name='packagehandoverdocument__packagehandoverdocumentmedia__status',
        widget=QueryArrayWidget,
        choices=PackageHandoverDocumentMedia.Status.choices,
        method='filter_by_status'
    )

    def filter_by_status(self, queryset, name, value):
        return self.__filter_by_not_deleted_package_handover_document(queryset, name, value)

    def __filter_by_not_deleted_package_handover_document(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, packagehandoverdocument__deleted__isnull=True).distinct()
        return queryset

    def __filter_by_not_deleted_package_matrix(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, package_matrix__deleted__isnull=True).distinct()
        return queryset

    class Meta:
        model = PackageHandover
        fields = ('package_matrix',)
