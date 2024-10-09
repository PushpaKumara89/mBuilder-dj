from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.serializers.asset_handover.asset_handover_document_media_update.asset_handover_document_media_update_bulk_create_serializer import \
    AssetHandoverDocumentMediaUpdateBulkCreateSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandoverDocumentMediaUpdate
from api.permissions import IsSuperuser, IsProjectClient, IsProjectSubcontractor, IsCompanyAdmin, IsProjectAdmin, \
    IsProjectManager
from api.permissions.asset_handover_document_media_bulk_update.is_able_to_use_by_subcontractor import \
    IsAbleToUseBySubcontractor
from api.services.asset_handover_document_media_update_service import AssetHandoverDocumentMediaUpdateService


class AssetHandoverDocumentMediaUpdateBulkViewSet(BaseViewSet, CreateModelMixin):
    _request_permissions = {
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | (IsProjectSubcontractor & IsAbleToUseBySubcontractor),),
    }

    serializer_class = AssetHandoverDocumentMediaUpdateBulkCreateSerializer
    queryset = AssetHandoverDocumentMediaUpdate.objects.all()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['asset_handover_document'] = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AssetHandoverDocumentMediaUpdateService.create_bulk_updates(serializer.validated_data,
                                                                               serializer.context)
        return Response(result, status=status.HTTP_201_CREATED)
