from rest_framework.permissions import BasePermission

from api.models import User, PackageHandoverDocumentType, PackageHandoverDocumentGroup


class IsAbleToBulkCreateBySubcontractor(BasePermission):
    def has_permission(self, request, view):
        package_handover_document_type_pk = request.data.get('package_handover_document_type')

        return PackageHandoverDocumentType.objects.filter(
            pk=package_handover_document_type_pk,
            group__pk__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(User.Group.SUBCONTRACTOR.value)
        ).exists()
