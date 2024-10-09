from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey
from api.http.filters.package_handover_document_media_filter import PackageHandoverDocumentMediaFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import PackageHandoverDocumentMediaSerializer
from api.http.serializers.package_handover.package_handover_document_media.package_handover_document_media_batch_download_serializer import \
    PackageHandoverDocumentMediaBatchDownloadSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, PackageHandoverDocumentGroup
from api.models.package_handover.package_handover_document_media import PackageHandoverDocumentMedia
from api.permissions import IsProjectUser, IsSuperuser, IsProjectStaff, IsProjectClient, IsProjectConsultant, \
    IsProjectSubcontractor, IsProjectAdmin, IsProjectManager
from api.permissions.package_handover_document_media import IsAbleToCreateBySubcontractor, IsAbleToCreateByConsultant, \
    IsAbleToUseBySubcontractor, IsAbleToUseByConsultant
from api.permissions.permission_group import PermissionGroup
from api.queues.send_report import send_handover_information_csv_report
from api.services.handover_document_media_download_service import HandoverDocumentMediaDownloadService
from api.utilities.package_handover_document_media_utilities import get_consultant_company_filter_query
from api.utilities.tasks_utilities import SerializableRequest


class PackageHandoverDocumentMediaViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'create': (
            HasAPIKey |
            PermissionGroup(
                IsAuthenticated,
                (IsSuperuser | IsProjectStaff) |
                (IsProjectConsultant & IsAbleToCreateByConsultant) |
                (IsProjectSubcontractor & IsAbleToCreateBySubcontractor)
            ),
        ),
        'retrieve': (
            HasAPIKey |
            PermissionGroup(
                IsAuthenticated,
                (IsSuperuser | IsProjectStaff | IsProjectClient |
                 (IsProjectConsultant & IsAbleToUseByConsultant) |
                 (IsProjectSubcontractor & IsAbleToUseBySubcontractor))
            ),
        ),
        'list': (
            HasAPIKey |
            PermissionGroup(
                IsAuthenticated,
                (IsSuperuser | IsProjectUser)
            ),
        ),
        'destroy': (
            HasAPIKey |
            PermissionGroup(
                IsAuthenticated,
                (IsSuperuser | IsProjectAdmin | IsProjectManager |
                 (IsProjectConsultant & IsAbleToUseByConsultant) |
                 (IsProjectSubcontractor & IsAbleToUseBySubcontractor))
            ),
        ),
        'generate_handover_information_csv': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'batch_download': (IsAuthenticated, IsSuperuser | IsProjectUser),
    }

    filterset_class = PackageHandoverDocumentMediaFilter
    serializer_class = PackageHandoverDocumentMediaSerializer
    queryset = PackageHandoverDocumentMedia.objects.all()
    search_fields = ['uid', 'information', 'media__name']

    def get_queryset(self):
        kwfilters = {
            'package_handover_document__package_handover__deleted__isnull': True
        }
        filters = []

        if self.request.user.is_consultant:
            filters.append(
                get_consultant_company_filter_query(self.request.user)
            )

        return self.queryset.filter(*filters, **kwfilters).distinct()

    def list(self, request, *args, **kwargs):
        user = request.user
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))

        if user.is_subcontractor:
            self.queryset = self.queryset.filter(
                packagehandoverdocumentmediaupdate__user__company_id=user.company_id,
                package_handover_document__package_handover__package_matrix__packagematrixcompany__company_id=user.company_id,
                package_handover_document__package_handover__package_matrix__deleted__isnull=True,
                package_handover_document__package_handover__deleted__isnull=True,
                package_handover_document__deleted__isnull=True
            )

        if user.is_subcontractor or user.is_consultant:
            self.queryset = self.queryset.filter(
                package_handover_document__package_handover_document_type__group__pk__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(user.group.pk),
                package_handover_document__package_handover__package_matrix__project__pk=project.pk,
                package_handover_document__package_handover__package_matrix__deleted__isnull=True,
                package_handover_document__package_handover__deleted__isnull=True,
                package_handover_document__deleted__isnull=True
            )
        else:
            self.queryset = self.queryset.filter(
                package_handover_document__package_handover__package_matrix__project__pk=project.pk,
                package_handover_document__package_handover__package_matrix__deleted__isnull=True,
                package_handover_document__package_handover__deleted__isnull=True,
                package_handover_document__deleted__isnull=True
            )

        return super().list(request, *args, **kwargs)

    def generate_handover_information_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])

        serializable_request = SerializableRequest(request)
        send_handover_information_csv_report(serializable_request, PackageHandoverDocumentMedia,
                                             project.pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def batch_download(self, request, *args, **kwargs):
        serializer = PackageHandoverDocumentMediaBatchDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = HandoverDocumentMediaDownloadService()
        saved_archive = service.save_archive(
            serializer.validated_data, HandoverDocumentMediaDownloadService.Entity.PACKAGE_HANDOVER_DOCUMENT_MEDIA)
        service.send_archive(saved_archive, kwargs['project_pk'], request.user)

        return Response(status=status.HTTP_200_OK)
