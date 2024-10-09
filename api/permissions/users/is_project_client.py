from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import Project


class IsProjectClient(BasePermission):
    message = _('You\'re not a project client.')

    def has_permission(self, request, view):
        user = request.user

        return user.is_client and Project.objects.filter(pk=view.kwargs['project_pk'], users__pk=user.pk).exists()
