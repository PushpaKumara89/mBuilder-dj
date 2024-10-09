from rest_framework.permissions import BasePermission

from api.models import PackageHandoverDocumentMedia


class CanClientDownloadPackageHandoverDocumentMedia(BasePermission):
    def has_permission(self, request, view):
        package_handover_document_media = PackageHandoverDocumentMedia.objects.filter(pk=view.kwargs['pk']).first()

        if package_handover_document_media:
            return package_handover_document_media.status in [PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                                                              PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                                                              PackageHandoverDocumentMedia.Status.ACCEPTED]

        return True
