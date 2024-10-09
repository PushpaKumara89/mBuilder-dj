from django.db.models import Q
from django.db.models.expressions import F, OuterRef, Exists
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import PackageHandoverDocumentMedia, PackageHandoverDocument, PackageHandoverDocumentType, \
    PackageHandoverDocumentGroup, PackageActivity, Package, Company, PackageHandoverDocumentMediaUpdate


class PackageHandoverDocumentMediaFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )
    company = rest_framework.ModelMultipleChoiceFilter(
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_company'
    )

    def filter_by_company(self, queryset, name, value):
        if value:
            return queryset \
                .filter(
                    Exists(PackageHandoverDocumentMediaUpdate.objects.filter(
                        ~Q(old_data__media=F('new_data__media')) | Q(old_data={}),
                        package_handover_document_media=OuterRef('id'),
                        company__in=value,
                        company__deleted__isnull=True,
                        deleted__isnull=True,
                    )),
                )
        return queryset

    package_handover_document = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document',
        queryset=PackageHandoverDocument.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_handover_document'
    )

    def filter_by_package_handover_document(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                '%s__deleted__isnull' % field: True
            }
            return queryset.filter(**filters)
        return queryset

    package_handover_document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document__package_handover_document_type',
        queryset=PackageHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_handover_document_type'
    )

    def filter_by_package_handover_document_type(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'package_handover_document__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    package_handover_document_group = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document__package_handover_document_type__group',
        queryset=PackageHandoverDocumentGroup.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_handover_document_group'
    )

    def filter_by_package_handover_document_group(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'package_handover_document__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document__package_handover__package_matrix__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_matrix_field'
    )

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='package_handover_document__package_handover__package_matrix__package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_matrix_field'
    )

    def filter_by_package_matrix_field(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'package_handover_document__deleted__isnull': True,
                'package_handover_document__package_handover__deleted__isnull': True,
                'package_handover_document__package_handover__package_matrix__deleted__isnull': True
            }
            return queryset.filter(**filters)

        return queryset

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        widget=QueryArrayWidget,
        choices=PackageHandoverDocumentMedia.Status.choices,
    )

    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('package_handover_document', 'status',)
