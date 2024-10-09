from django_filters import rest_framework

from api.models.asset_handover import AssetHandoverDocumentMediaUpdate


class AssetHandoverDocumentMediaUpdateFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )

    class Meta:
        model = AssetHandoverDocumentMediaUpdate
        fields = ('asset_handover_document_media', 'user',)
