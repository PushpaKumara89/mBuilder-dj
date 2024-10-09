from rest_framework.permissions import BasePermission

from api.models import PackageHandoverDocumentType, PackageHandoverDocumentGroup


class IsAbleToBulkCreateByConsultant(BasePermission):
    def has_permission(self, request, view):
        package_handover_document_type_pk = request.data.get('package_handover_document_type')

        return PackageHandoverDocumentType.objects.filter(
                   pk=package_handover_document_type_pk,
                   group__pk__in=[
                       PackageHandoverDocumentGroup.Group.CONSULTANT_DOCUMENT.value,
                       PackageHandoverDocumentGroup.Group.H_AND_S_CONSULTANT_DOCUMENT.value
                   ]
               ).exists()
