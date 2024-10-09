from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _


class IsSuperuser(BasePermission):
    message = _('You\'re not a superuser.')

    def has_permission(self, request, view):
        return request.user.is_superuser
