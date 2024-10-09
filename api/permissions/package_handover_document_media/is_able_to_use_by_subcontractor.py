from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import User, PackageHandoverDocumentMedia, PackageHandoverDocumentGroup


class IsAbleToUseBySubcontractor(BasePermission):
    message = _('The subcontractor isn\'t able to use current document group')

    def has_permission(self, request, view):
        bulk = isinstance(request.data, list)

        if bulk:
            for data_update in request.data:
                package_handover_document_media_pk = data_update['package_handover_document_media']

                result = self.__check_permission(package_handover_document_media_pk)
                if not result:
                    return False

            return True
        else:
            package_handover_document_media_pk = view.kwargs.get('media_pk') if view.kwargs.get(
                'media_pk') is not None else view.kwargs.get('pk')

            return self.__check_permission(package_handover_document_media_pk)

    def __check_permission(self, package_handover_document_media_pk):
        return PackageHandoverDocumentMedia.objects.filter(
                   pk=package_handover_document_media_pk,
                   package_handover_document__package_handover_document_type__group__pk__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(User.Group.SUBCONTRACTOR.value)
               ).exists()
