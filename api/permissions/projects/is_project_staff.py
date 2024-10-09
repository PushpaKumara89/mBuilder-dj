from rest_framework.permissions import BasePermission

from api.models import Project


class IsProjectStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_pk = view.kwargs.get('pk')

        return Project.objects.filter(users__pk=user.id, pk=project_pk, users__is_staff=True).exists()
