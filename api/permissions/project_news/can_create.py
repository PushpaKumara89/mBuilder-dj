from rest_framework.permissions import BasePermission

from api.models import Project


class CanCreate(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_pk = request.data.get('project_id')

        return Project.objects.filter(users__pk=user.pk, pk=project_pk).exists()
