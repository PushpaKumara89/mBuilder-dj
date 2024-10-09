from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.media_filter import MediaFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.media.media_serializer import MediaSerializer
from api.http.views.view import BaseViewSet
from api.models import Media, AssetHandoverDocumentMedia, PackageHandoverDocumentMedia, Project, HandoverDocument
from api.permissions import IsSuperuser, IsCompanyAdmin, IsProjectAdmin, IsProjectManager, IsProjectSubcontractor, \
    IsProjectConsultant, IsProjectClient, CanClientDownloadAssetHandoverDocumentMedia, \
    CanClientDownloadPackageHandoverDocumentMedia, IsProjectUser
from api.permissions.is_staff import IsStaff
from api.permissions.not_allow_any import NotAllowAny
from api.permissions.permission_group import PermissionGroup
from api.services.media_entity_service import MediaEntityService
from api.storages import AzurePrivateReportStorage, AzurePrivateProjectSnapshotStorage


class MediaViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | AllowAny,),
        'retrieve_private': (HasAPIKey | AllowAny,),
        'retrieve_handover_document_media': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectUser),),
        'retrieve_package_handover_document_media': (
            IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectSubcontractor | IsProjectConsultant | (IsProjectClient & CanClientDownloadPackageHandoverDocumentMedia)),
        ),
        'retrieve_asset_handover_document_media': (
            IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectSubcontractor | IsProjectConsultant | (IsProjectClient & CanClientDownloadAssetHandoverDocumentMedia)),
        ),
        'retrieve_private_report': (HasAPIKey | AllowAny,),
        'retrieve_private_project_snapshot': (HasAPIKey | IsSuperuser | IsStaff,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsStaff,),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (AllowAny,),
        'bulk_create': (AllowAny,),
        'partial_update': (NotAllowAny,),
        'update': (IsAuthenticated, IsStaff,),
        'create_plan': (IsAuthenticated, IsSuperuser | IsStaff),
    }

    serializer_class = MediaSerializer
    queryset = Media.objects.all()
    filterset_class = MediaFilter

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        MediaEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = MediaEntityService().create(serializer.validated_data)

        return Response(self.get_serializer(media).data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def bulk_create(self, request, *args, **kwargs):
        files = [{'local_id': local_id, 'file': value, 'is_public': False} for local_id, value in request.data.items()]

        serializer = self.get_serializer(data=files, many=True)
        serializer.is_valid(raise_exception=True)
        objects = [MediaEntityService().create(validated_data) for validated_data in serializer.validated_data]

        return Response(self.get_serializer(objects, many=True, expand=['expanded_project_snapshot_thumbnails.expanded_thumbnail']).data,
                        status=status.HTTP_201_CREATED)

    def retrieve_private(self, request, *args, **kwargs):
        media = get_object_or_404(self.get_queryset().filter(hash=kwargs['uuid']))

        return self._get_private_media(media)

    @action(methods=['post'], detail=False, url_path='plan')
    def create_plan(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = MediaEntityService().create(serializer.validated_data, create_thumbnail=False)

        return Response(self.get_serializer(media).data, status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))

    def retrieve_package_handover_document_media(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['project_pk'])
        package_handover_document_media = get_object_or_404(
            PackageHandoverDocumentMedia.objects.all(),
            pk=kwargs['pk'], package_handover_document__package_handover__package_matrix__project_id=project.pk
        )
        media = get_object_or_404(self.get_queryset(), pk=package_handover_document_media.media_id)

        return self._get_private_media(media)

    def retrieve_asset_handover_document_media(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['project_pk'])
        asset_handover_document_media = get_object_or_404(
            AssetHandoverDocumentMedia.objects.all(),
            pk=kwargs['pk'], asset_handover_document__asset_handover__location_matrix__project_id=project.pk
        )
        media = get_object_or_404(self.get_queryset(), pk=asset_handover_document_media.media_id)

        return self._get_private_media(media)

    def _get_private_media(self, media):
        storage = media.get_common_storage()
        link = storage.url(media.original_link)

        return HttpResponseRedirect(redirect_to=link)

    def retrieve_private_report(self, request, *args, **kwargs):
        media = get_object_or_404(self.get_queryset().filter(hash=kwargs['uuid']))
        storage = default_storage if media.is_public else AzurePrivateReportStorage()
        link = storage.url(media.original_link)

        return HttpResponseRedirect(redirect_to=link)

    def retrieve_private_project_snapshot(self, request, *args, **kwargs):
        media = get_object_or_404(self.get_queryset().filter(hash=kwargs['uuid']))
        storage = AzurePrivateProjectSnapshotStorage()
        link = storage.url(media.original_link)

        return HttpResponseRedirect(redirect_to=link)

    def retrieve_handover_document_media(self, request, *args, **kwargs):
        handover_document = get_object_or_404(HandoverDocument.objects.all(), pk=kwargs['pk'], project=kwargs['project_pk'])
        return self._get_private_media(handover_document.media)
