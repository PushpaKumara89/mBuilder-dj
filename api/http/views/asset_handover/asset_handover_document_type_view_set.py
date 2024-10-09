from rest_framework.permissions import IsAuthenticated

from api.http.filters.asset_handover.asset_handover_document_type_filter import AssetHandoverDocumentTypeFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_type_serializer import \
    AssetHandoverDocumentTypeSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandoverDocumentType
from api.permissions import IsSuperuser, IsManager, IsAdmin, IsCompanyAdmin


class AssetHandoverDocumentTypeViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = AssetHandoverDocumentTypeSerializer
    queryset = AssetHandoverDocumentType.objects.all()
    filterset_class = AssetHandoverDocumentTypeFilter
    search_fields = ['name']
