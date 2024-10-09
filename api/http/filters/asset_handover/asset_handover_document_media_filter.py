from django.db.models import Q, F, Exists, OuterRef
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.non_validating_multiple_choice_filter import NonValidatingMultipleChoiceFilter
from api.models import AssetHandoverDocumentMedia, AssetHandoverDocument, AssetHandoverDocumentType, AssetHandover, \
    PackageActivity, Package, Company, AssetHandoverDocumentMediaUpdate


class AssetHandoverDocumentMediaFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('asset_handover_document', 'asset_handover_document',),
            ('media', 'media',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='assethandoverdocumentmediaupdate__company',
        queryset=Company.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_company'
    )

    def filter_by_company(self, queryset, name, value):
        if value:
            return queryset.filter(
                Exists(
                    AssetHandoverDocumentMediaUpdate.objects.filter(
                        ~Q(old_data__media=F('new_data__media')) | Q(old_data={}),
                        asset_handover_document_media_id=OuterRef('id'),
                        company__in=value,
                        company__deleted__isnull=True,
                        deleted__isnull=True,
                    )
                )
            )
        return queryset

    asset_handover_document = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover_document',
        queryset=AssetHandoverDocument.objects.all(),
        widget=QueryArrayWidget,
    )

    asset_handover_document_type = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover_document__document_type',
        queryset=AssetHandoverDocumentType.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_asset_handover_document_type'
    )

    def filter_by_asset_handover_document_type(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'asset_handover_document__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    asset_handover = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover',
        queryset=AssetHandover.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_asset_handover'
    )

    def filter_by_asset_handover(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'asset_handover_document__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover__package_activity',
        queryset=PackageActivity.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package_activity'
    )

    def filter_by_package_activity(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'asset_handover_document__deleted__isnull': True,
                'asset_handover_document__asset_handover__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover__package_activity__packagematrix__package',
        queryset=Package.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_package'
    )

    def filter_by_package(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'asset_handover_document__deleted__isnull': True,
                'asset_handover_document__asset_handover__deleted__isnull': True,
                'asset_handover_document__asset_handover__package_activity__packagematrix__deleted__isnull': True
            }
            if 'project_pk' in self.request.parser_context['kwargs']:
                filters['asset_handover_document__asset_handover__package_activity__packagematrix__project'] = self.request.parser_context['kwargs']['project_pk']
            return queryset.filter(**filters)
        return queryset

    building = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover__location_matrix__building',
        widget=QueryArrayWidget,
        method='filter_by_location_matrix_field'
    )
    level = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover__location_matrix__level',
        widget=QueryArrayWidget,
        method='filter_by_location_matrix_field'
    )
    area = NonValidatingMultipleChoiceFilter(
        field_name='asset_handover_document__asset_handover__location_matrix__area',
        widget=QueryArrayWidget,
        method='filter_by_location_matrix_field'
    )

    def filter_by_location_matrix_field(self, queryset, field, value):
        if value:
            filters = {
                '%s__in' % field: value,
                'asset_handover_document__deleted__isnull': True,
                'asset_handover_document__asset_handover__deleted__isnull': True,
                'asset_handover_document__asset_handover__location_matrix__deleted__isnull': True
            }
            return queryset.filter(**filters)
        return queryset

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        widget=QueryArrayWidget,
        choices=AssetHandoverDocumentMedia.Status.choices,
    )

    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('media',)
