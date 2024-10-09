from rest_framework.permissions import BasePermission

from api.models import Project


class IsProjectUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_pk = view.kwargs.get('project_pk', request.query_params.getlist('project'))
        if type(project_pk) is not list:
            project_pk = [project_pk]

        return Project.objects.filter(pk__in=project_pk, users__pk=user.pk).exists()
