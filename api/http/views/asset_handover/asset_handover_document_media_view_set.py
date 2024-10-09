from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.asset_handover.asset_handover_document_media_filter import AssetHandoverDocumentMediaFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_batch_download_serializer import \
    AssetHandoverDocumentMediaBatchDownloadSerializer
from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_serializer import AssetHandoverDocumentMediaSerializer
from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_bulk_serializer import AssetHandoverDocumentMediaBulkSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandoverDocumentMedia, Project
from api.permissions import IsSuperuser, IsProjectSubcontractor, IsProjectConsultant, IsProjectAdmin, \
    IsProjectManager, IsProjectClient, IsCompanyAdmin, IsProjectUser
from api.permissions.asset_handover_document_media import IsAbleToUseBySubcontractor, IsAbleToCreateBySubcontractor
from api.queues.send_report import send_handover_information_csv_report
from api.services.handover_document_media_download_service import HandoverDocumentMediaDownloadService
from api.utilities.tasks_utilities import SerializableRequest


class AssetHandoverDocumentMediaViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | IsProjectSubcontractor | IsProjectConsultant,),
        'retrieve': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | (IsProjectSubcontractor & IsAbleToUseBySubcontractor) | IsProjectConsultant,),
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | (IsProjectSubcontractor & IsAbleToCreateBySubcontractor),),
        'bulk_create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectSubcontractor,),
        'destroy': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | (IsProjectSubcontractor & IsAbleToUseBySubcontractor),),
        'generate_handover_information_csv': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'batch_download': (IsAuthenticated, IsSuperuser | IsProjectUser),
    }

    serializer_class = AssetHandoverDocumentMediaSerializer
    queryset = AssetHandoverDocumentMedia.objects.all()
    filterset_class = AssetHandoverDocumentMediaFilter
    search_fields = ['uid', 'media__name']

    def get_queryset(self):
        filters = {
            'asset_handover_document__asset_handover__project': self.kwargs['project_pk'],
            'asset_handover_document__deleted__isnull': True,
            'asset_handover_document__asset_handover__deleted__isnull': True
        }

        if self.request.user.is_subcontractor:
            filters['asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__company'] = self.request.user.company
            filters['assethandoverdocumentmediaupdate__user__company'] = self.request.user.company
        elif self.request.user.is_consultant:
            filters['status'] = AssetHandoverDocumentMedia.Status.ACCEPTED
        elif self.request.user.is_client:
            filters['status__in'] = [AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                                     AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                                     AssetHandoverDocumentMedia.Status.ACCEPTED]

        return self.queryset.filter(**filters).distinct()

    def bulk_create(self, request, *args, **kwargs):
        serializer = AssetHandoverDocumentMediaBulkSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        created_media = serializer.create(serializer.validated_data)

        return Response(data=created_media, status=status.HTTP_201_CREATED)

    def generate_handover_information_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])

        serializable_request = SerializableRequest(request)
        send_handover_information_csv_report(serializable_request, AssetHandoverDocumentMedia,
                                             project.pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def batch_download(self, request, *args, **kwargs):
        serializer = AssetHandoverDocumentMediaBatchDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = HandoverDocumentMediaDownloadService()
        saved_archive = service.save_archive(
            serializer.validated_data, HandoverDocumentMediaDownloadService.Entity.ASSET_HANDOVER_DOCUMENT_MEDIA)
        service.send_archive(saved_archive, kwargs['project_pk'], request.user)

        return Response(status=status.HTTP_200_OK)
