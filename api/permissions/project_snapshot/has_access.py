from rest_framework.permissions import BasePermission

from api.models import Project


class HasAccess(BasePermission):
    def has_permission(self, request, view):
        return Project.objects.filter(users=request.user, pk=view.kwargs.get('pk')).exists()
