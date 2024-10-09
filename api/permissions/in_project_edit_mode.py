from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from api.models import EditMode


class InProjectEditMode(BasePermission):
    message = _('You have to be in the Edit mode.')

    def has_permission(self, request, view):
        user = request.user

        return EditMode.objects.filter(user=user, project__pk=view.kwargs.get('project_pk')).exists()
