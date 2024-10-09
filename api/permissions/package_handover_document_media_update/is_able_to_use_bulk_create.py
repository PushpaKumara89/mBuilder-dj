from django.db.models import Q

from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import PackageHandoverDocumentGroup, PackageHandoverDocument


class IsAbleToUseBulkCreate(BasePermission):
    message = _('You\'re not able to use current document group')

    def has_permission(self, request, view):
        package_handover_document_pk = view.kwargs.get('pk')
        document_group = PackageHandoverDocumentGroup.GROUPS_MAP.get(request.user.group_id)
        if document_group:
            filters = [
                Q(
                    id=package_handover_document_pk,
                    package_handover_document_type__group__pk__in=document_group
                ),
            ]

            return PackageHandoverDocument.objects.filter(*filters).exists()

        return True
