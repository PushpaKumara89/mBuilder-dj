from rest_framework.permissions import BasePermission
from api.models import ProjectUser


class CanClientSeeProjectSubtasks(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_client and \
            ProjectUser.objects.filter(
                project_id=view.kwargs.get('project_pk'),
                user=request.user,
                project__is_subtask_visible_for_clients=True
            ).exists()
