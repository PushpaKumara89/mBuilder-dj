from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from api.models import AssetHandoverDocument


class IsAbleToCreateBySubcontractor(BasePermission):
    message = _('The subcontractor isn\'t able to use current document')

    def has_permission(self, request, view):
        asset_handover_document_pk = request.data.get('asset_handover_document')

        return AssetHandoverDocument.objects.filter(
                   pk=asset_handover_document_pk,
                   asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__company=request.user.company
               ).exists()
