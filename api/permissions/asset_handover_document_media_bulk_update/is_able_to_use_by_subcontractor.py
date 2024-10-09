from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from api.models import AssetHandoverDocument


class IsAbleToUseBySubcontractor(BasePermission):
    message = _('The subcontractor isn\'t able to use current document media')

    def has_permission(self, request, view):
        return AssetHandoverDocument.objects.filter(
            pk=view.kwargs.get('pk'),
            asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__company=request.user.company,
            asset_handover__location_matrix__locationmatrixpackage__package_matrix__packagematrixcompany__deleted__isnull=True,
            asset_handover__location_matrix__locationmatrixpackage__package_matrix__deleted__isnull=True,
            asset_handover__location_matrix__deleted__isnull=True,
            asset_handover__deleted__isnull=True,
        ).exists()
