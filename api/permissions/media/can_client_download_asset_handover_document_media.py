from rest_framework.permissions import BasePermission

from api.models import AssetHandoverDocumentMedia


class CanClientDownloadAssetHandoverDocumentMedia(BasePermission):
    def has_permission(self, request, view):
        asset_handover_document_media = AssetHandoverDocumentMedia.objects.filter(pk=view.kwargs['pk']).first()

        if asset_handover_document_media:
            return asset_handover_document_media.status in [AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                                                              AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                                                              AssetHandoverDocumentMedia.Status.ACCEPTED]

        return True
