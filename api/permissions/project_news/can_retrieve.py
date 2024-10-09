from rest_framework.permissions import BasePermission

from api.models import Project


class CanRetrieve(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_news__pk = view.kwargs.get('pk')

        return Project.objects.filter(users__pk=user.pk, projectnews__pk=project_news__pk).exists()
