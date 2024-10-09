from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import User, PackageHandoverDocument, PackageHandoverDocumentGroup


class IsAbleToCreateBySubcontractor(BasePermission):
    message = _('The subcontractor isn\'t able to manage current document group')

    def has_permission(self, request, view):
        package_handover_document_pk = request.data.get('package_handover_document')

        return PackageHandoverDocument.objects.filter(
                   pk=package_handover_document_pk,
                   package_handover_document_type__group__pk__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(User.Group.SUBCONTRACTOR.value),
                   package_handover__package_matrix__packagematrixcompany__company=request.user.company
               ).exists()
