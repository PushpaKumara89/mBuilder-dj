from rest_framework.permissions import BasePermission

from api.models import Project


class IsAllowedForClient(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_client:
            return Project.objects.filter(pk__in=request.query_params.getlist('project'),
                                          is_task_visible_for_clients=True).exists()
        return True