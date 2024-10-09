from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_bulk_create_serializer import \
    PackageHandoverDocumentMediaUpdateBulkCreateSerializer
from api.http.views.view import BaseViewSet
from api.models.package_handover.package_handover_document_media_update import PackageHandoverDocumentMediaUpdate
from api.permissions import IsSuperuser, IsProjectStaff, IsProjectClient, IsProjectConsultant, IsProjectSubcontractor
from api.permissions.package_handover_document_media_update.is_able_to_use_bulk_create import IsAbleToUseBulkCreate
from api.permissions.permission_group import PermissionGroup
from api.services.package_handover_document_media_update_service import PackageHandoverDocumentMediaUpdateService


class PackageHandoverDocumentMediaUpdateBulkViewSet(BaseViewSet, CreateModelMixin):
    _request_permissions = {
        'create': (HasAPIKey | PermissionGroup(
            IsAuthenticated,
            (IsSuperuser |
             IsProjectStaff |
             IsProjectClient |
             (IsProjectConsultant & IsAbleToUseBulkCreate) |
             (IsProjectSubcontractor & IsAbleToUseBulkCreate)
             ),),),
    }

    serializer_class = PackageHandoverDocumentMediaUpdateBulkCreateSerializer
    queryset = PackageHandoverDocumentMediaUpdate.objects.all()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['package_handover_document'] = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = PackageHandoverDocumentMediaUpdateService.create_bulk_updates(serializer.validated_data, serializer.context)
        return Response(result, status=status.HTTP_201_CREATED)
