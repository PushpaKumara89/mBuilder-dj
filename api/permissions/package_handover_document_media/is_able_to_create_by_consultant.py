from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import PackageHandoverDocument, PackageHandoverDocumentGroup


class IsAbleToCreateByConsultant(BasePermission):
    message = _('The consultant isn\'t able to manage current document group')

    def has_permission(self, request, view):
        package_handover_document_pk = request.data.get('package_handover_document')

        return PackageHandoverDocument.objects.filter(
                   pk=package_handover_document_pk,
                   package_handover_document_type__group__pk__in=[
                       PackageHandoverDocumentGroup.Group.CONSULTANT_DOCUMENT.value,
                       PackageHandoverDocumentGroup.Group.H_AND_S_CONSULTANT_DOCUMENT.value
                   ]
               ).exists()
