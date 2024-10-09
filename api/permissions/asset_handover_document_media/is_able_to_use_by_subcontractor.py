from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from api.models import AssetHandoverDocumentMedia


class IsAbleToUseBySubcontractor(BasePermission):
    message = _('The subcontractor isn\'t able to use current document media')

    def has_permission(self, request, view):
        asset_handover_document_media_pk = view.kwargs.get('media_pk') if view.kwargs.get(
                'media_pk') is not None else view.kwargs.get('pk')

        return AssetHandoverDocumentMedia.objects.filter(
                   pk=asset_handover_document_media_pk,
                   asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__company=request.user.company
               ).exists()
