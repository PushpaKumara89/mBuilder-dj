from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters.asset_handover.asset_handover_document_filter import AssetHandoverDocumentFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import AssetHandoverDocumentSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandoverDocument
from api.permissions import IsSuperuser, IsManager, IsAdmin, IsCompanyAdmin, IsProjectSubcontractor, IsProjectClient, \
    IsProjectConsultant


class AssetHandoverDocumentViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager | IsProjectSubcontractor | IsProjectClient | IsProjectConsultant,),
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
        'destroy': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = AssetHandoverDocumentSerializer
    queryset = AssetHandoverDocument.objects.all()
    filterset_class = AssetHandoverDocumentFilter

    def get_queryset(self):
        filters = {}

        if self.request.user.is_subcontractor:
            filters['asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__company'] = self.request.user.company

        return self.queryset.filter(**filters)
