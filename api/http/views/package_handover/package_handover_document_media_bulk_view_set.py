from rest_framework import mixins
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.serializers import PackageHandoverDocumentMediaBulkCreateSerializer
from api.http.views.view import BaseViewSet
from api.models import Project
from api.models.package_handover.package_handover_document_media import PackageHandoverDocumentMedia
from api.permissions import IsSuperuser, IsProjectStaff, IsProjectConsultant, \
    IsProjectSubcontractor
from api.permissions.package_handover_document_media import IsAbleToBulkCreateBySubcontractor, \
    IsAbleToBulkCreateByConsultant
from api.permissions.permission_group import PermissionGroup


class PackageHandoverDocumentMediaBulkViewSet(BaseViewSet, mixins.CreateModelMixin):
    _request_permissions = {
        'create': (HasAPIKey | PermissionGroup(
            IsAuthenticated,
            (IsSuperuser | IsProjectStaff) |
            (IsProjectConsultant & IsAbleToBulkCreateByConsultant) |
            (IsProjectSubcontractor & IsAbleToBulkCreateBySubcontractor)
        ),),
    }

    serializer_class = PackageHandoverDocumentMediaBulkCreateSerializer
    queryset = PackageHandoverDocumentMedia.objects.all()

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))

        request.data['project'] = project.pk
        package_handover_document_media_bulk_create_serializer = self.get_serializer(data=request.data, context={'request': self.request})
        package_handover_document_media_bulk_create_serializer.is_valid(raise_exception=True)

        package_handover_document_media = package_handover_document_media_bulk_create_serializer.bulk_create()

        return Response(data=package_handover_document_media, status=status.HTTP_201_CREATED)
