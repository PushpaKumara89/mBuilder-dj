from rest_framework.permissions import BasePermission

from api.models import Project


class IsProjectUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return Project.objects.filter(pk=view.kwargs.get('pk'), users__pk=user.pk).exists()
