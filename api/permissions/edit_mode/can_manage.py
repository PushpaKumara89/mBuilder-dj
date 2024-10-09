from rest_framework.permissions import BasePermission

from api.models import Project, EditMode


class CanManage(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        edit_mode_project = EditMode.objects.filter(project=view.kwargs.get('project_pk'))
        exists = edit_mode_project.exists()

        return \
            (user.is_superuser or Project.objects.filter(pk=view.kwargs.get('project_pk'), users=user, users__is_staff=True).exists()) \
            and \
            (not exists or (exists and edit_mode_project.first().user.pk == user.pk))
