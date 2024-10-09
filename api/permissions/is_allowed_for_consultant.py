from rest_framework.permissions import BasePermission

from api.models import Project


class IsAllowedForConsultant(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_consultant:
            return Project.objects.filter(pk=view.kwargs.get('project_pk'),
                                          is_task_visible_for_clients=True).exists()
        return True