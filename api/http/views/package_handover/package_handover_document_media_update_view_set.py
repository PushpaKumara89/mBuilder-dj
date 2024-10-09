from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters import PackageHandoverDocumentMediaUpdateFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import PackageHandoverDocumentMediaUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, PackageHandoverDocumentGroup, PackageHandoverDocumentMedia
from api.models.package_handover.package_handover_document_media_update import \
    PackageHandoverDocumentMediaUpdate
from api.permissions import IsSuperuser, IsProjectStaff, IsProjectClient, IsProjectConsultant, \
    IsProjectSubcontractor
from api.permissions.package_handover_document_media import IsAbleToUseBySubcontractor, IsAbleToUseByConsultant
from api.permissions.permission_group import PermissionGroup


class PackageHandoverDocumentMediaUpdateViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'create': (HasAPIKey | PermissionGroup(
            IsAuthenticated,
            (IsSuperuser |
             IsProjectStaff |
             IsProjectClient |
             (IsProjectConsultant & IsAbleToUseByConsultant) |
             (IsProjectSubcontractor & IsAbleToUseBySubcontractor)
             ),),),
        'retrieve': (HasAPIKey | PermissionGroup(
            IsAuthenticated,
            (IsSuperuser | IsProjectStaff | IsProjectClient |
             (IsProjectConsultant & IsAbleToUseByConsultant) |
             (IsProjectSubcontractor & IsAbleToUseBySubcontractor)
             ),),),
        'list': (HasAPIKey | PermissionGroup(
            IsAuthenticated,
            (IsSuperuser | IsProjectStaff | IsProjectClient |
             (IsProjectConsultant & IsAbleToUseByConsultant) |
             (IsProjectSubcontractor & IsAbleToUseBySubcontractor)
             ),),),
    }

    serializer_class = PackageHandoverDocumentMediaUpdateSerializer
    filterset_class = PackageHandoverDocumentMediaUpdateFilter
    queryset = PackageHandoverDocumentMediaUpdate.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(package_handover_document_media__pk=self.kwargs['media_pk'])

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['package_handover_document_media'] = kwargs['media_pk']

        package_handover_document_media_update = super().create(request, *args, **kwargs)

        if request.data.get('new_data', {}).get('status') == PackageHandoverDocumentMedia.Status.REMOVED:
            self.__remove_related_package_handover_document_media(request.data['package_handover_document_media'])

        return package_handover_document_media_update

    def list(self, request, *args, **kwargs):
        user = request.user
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))

        if user.is_subcontractor or user.is_consultant:
            self.queryset = self.queryset.filter(
                package_handover_document_media__package_handover_document__package_handover_document_type__group_id__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(user.group.pk),
                package_handover_document_media__package_handover_document__package_handover__package_matrix__project_id=project.pk
            )
        else:
            self.queryset = self.queryset.filter(
                package_handover_document_media__package_handover_document__package_handover__package_matrix__project_id=project.pk
            )

        return super().list(request, *args, **kwargs)

    def __remove_related_package_handover_document_media(self, package_handover_document_media_pk):
        package_handover_document_media = PackageHandoverDocumentMedia.objects.get(pk=package_handover_document_media_pk)

        package_handover_document_media.delete()
