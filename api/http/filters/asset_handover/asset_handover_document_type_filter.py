from django_filters import rest_framework

from api.models import AssetHandoverDocumentType


class AssetHandoverDocumentTypeFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name',),
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )

    class Meta:
        model = AssetHandoverDocumentType
        fields = ('name',)
