from django.db.models import Exists, OuterRef
from rest_framework.permissions import BasePermission

from api.models import EditMode, LocationMatrix


class InEditMode(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return EditMode.objects.filter(
            Exists(LocationMatrix.objects.filter(pk=view.kwargs.get('pk'), project=OuterRef('project'))),
            user=user
        ).exists()
