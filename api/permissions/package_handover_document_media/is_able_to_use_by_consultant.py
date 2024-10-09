from django.db.models import Q

from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import User, PackageHandoverDocumentMedia, PackageHandoverDocumentGroup
from api.utilities.package_handover_document_media_utilities import get_consultant_company_filter_query


class IsAbleToUseByConsultant(BasePermission):
    message = _('The consultant isn\'t able to use current document group')

    def has_permission(self, request, view):
        bulk = isinstance(request.data, list)

        if bulk:
            for data_update in request.data:
                package_handover_document_media_pk = data_update['package_handover_document_media']

                result = self.__check_permission(package_handover_document_media_pk, request)
                if not result:
                    return False

            return True
        else:
            package_handover_document_media_pk = view.kwargs.get('media_pk') if view.kwargs.get(
                'media_pk') is not None else view.kwargs.get('pk')

            return self.__check_permission(package_handover_document_media_pk, request)

    def __check_permission(self, package_handover_document_media_pk, request):
        filters = [
            Q(
                pk=package_handover_document_media_pk,
                package_handover_document__package_handover_document_type__group__pk__in=PackageHandoverDocumentGroup.GROUPS_MAP.get(
                    User.Group.CONSULTANT.value)
            ),
            get_consultant_company_filter_query(request.user)
        ]

        return PackageHandoverDocumentMedia.objects.filter(*filters).exists()

