from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.media.handover_document_media_batch_download_serializer import \
    HandoverDocumentMediaBatchDownloadSerializer
from api.http.views.view import BaseViewSet
from api.models import HandoverDocument
from api.permissions import IsSuperuser, IsProjectUser
from api.queues.handover_document import send_email_with_handover_document_archive
from api.services.handover_document_service import HandoverDocumentService
from api.services.media_entity_service import MediaEntityService


class HandoverDocumentMediaBatchDownloadViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'download': (IsAuthenticated, IsSuperuser | IsProjectUser),
    }

    serializer_class = HandoverDocumentMediaBatchDownloadSerializer
    queryset = HandoverDocument.objects.all()

    def download(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        handover_document_service = HandoverDocumentService()
        payload = handover_document_service.get_archive_with_media_to_save(serializer.validated_data)

        saved_archive = MediaEntityService().create(payload, create_thumbnail=False)
        send_email_with_handover_document_archive(saved_archive, kwargs['project_pk'], request.user)

        return Response(status=status.HTTP_200_OK)
