from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import User, AssetHandover, AssetHandoverDocumentType, AssetHandoverDocument, AssetHandoverDocumentMedia, Package, PackageActivity, Company


class AssetHandoverDocumentFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('asset_handover', 'asset_handover',),
            ('number_required_files', 'number_required_files',),
            ('document_type', 'document_type',),
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
                assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__in=value,
                assethandoverdocumentmedia__assethandoverdocumentmediaupdate__company__deleted__isnull=True,
                assethandoverdocumentmedia__assethandoverdocumentmediaupdate__deleted__isnull=True,
                assethandoverdocumentmedia__deleted__isnull=True,
            )
        return queryset

    asset_handover = rest_framework.ModelMultipleChoiceFilter(
        queryset=AssetHandover.objects.all(),
        field_name='asset_handover',
        widget=QueryArrayWidget,
        method='filter_by_asset_handover'
    )

    def filter_by_asset_handover(self, queryset, name, value):
        if value:
            return queryset.filter(**{f'{name}__in': value}, asset_handover__deleted__isnull=True).distinct()
        return queryset

    document_type = rest_framework.ModelMultipleChoiceFilter(
        queryset=AssetHandoverDocumentType.objects.all(),
        field_name='document_type',
        widget=QueryArrayWidget
    )

    building = CharInFilter(field_name='asset_handover__location_matrix__building', widget=QueryArrayWidget)
    area = CharInFilter(field_name='asset_handover__location_matrix__area', widget=QueryArrayWidget)
    level = CharInFilter(field_name='asset_handover__location_matrix__level', widget=QueryArrayWidget)

    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover__location_matrix__locationmatrixpackage__package',
        queryset=Package.all_objects.all(),
        widget=QueryArrayWidget
    )

    package_activity = rest_framework.ModelMultipleChoiceFilter(
        field_name='asset_handover__package_activity',
        queryset=PackageActivity.all_objects.all(),
        widget=QueryArrayWidget
    )

    user = rest_framework.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        widget=QueryArrayWidget,
        method='filter_by_user'
    )

    def filter_by_user(self, queryset, name, value):
        if value:
            return queryset.filter(
                assethandoverdocumentmedia__assethandoverdocumentmediaupdate__user__in=value,
                assethandoverdocumentmedia__assethandoverdocumentmediaupdate__new_data__status=AssetHandoverDocumentMedia.Status.IN_PROGRESS.value,
                asset_handover__deleted__isnull=True
            ).distinct()
        return queryset

    class Meta:
        model = AssetHandoverDocument
        fields = ('document_type',)
