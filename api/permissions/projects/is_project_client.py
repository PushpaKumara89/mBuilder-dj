from rest_framework.permissions import BasePermission

from api.models import Project


class IsProjectClient(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_pk = view.kwargs.get('pk')

        return user.is_client and Project.objects.filter(users__pk=user.id, pk=project_pk).exists()
