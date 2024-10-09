from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters.asset_handover.asset_handover_document_media_update_filter import \
    AssetHandoverDocumentMediaUpdateFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import AssetHandoverDocumentMediaUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models.asset_handover import AssetHandoverDocumentMediaUpdate
from api.permissions import IsSuperuser, IsProjectSubcontractor, IsProjectConsultant, IsProjectAdmin, IsProjectManager, \
    IsProjectClient, IsCompanyAdmin
from api.permissions.asset_handover_document_media import IsAbleToUseBySubcontractor


class AssetHandoverDocumentMediaUpdateViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | (IsProjectSubcontractor & IsAbleToUseBySubcontractor) | IsProjectConsultant,),
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | (IsProjectSubcontractor & IsAbleToUseBySubcontractor),),
        'retrieve': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | (IsProjectSubcontractor & IsAbleToUseBySubcontractor) | IsProjectConsultant,),
    }

    serializer_class = AssetHandoverDocumentMediaUpdateSerializer
    queryset = AssetHandoverDocumentMediaUpdate.objects.all()
    filterset_class = AssetHandoverDocumentMediaUpdateFilter

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['asset_handover_document_media'] = kwargs['media_pk']

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        filters = {}

        if project_pk := self.kwargs.get('project_pk'):
            filters['asset_handover_document_media__asset_handover_document__asset_handover__location_matrix__project_id'] = project_pk

        if media_pk := self.kwargs.get('media_pk'):
            filters['asset_handover_document_media_id'] = media_pk

        return self.queryset.filter(**filters)
