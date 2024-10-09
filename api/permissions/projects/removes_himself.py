from rest_framework.permissions import BasePermission

from api.models import Project


class RemovesHimself(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        project_pk = view.kwargs.get('pk')

        return Project.objects.filter(users__pk=user.id, pk=project_pk).exists() and \
               'users' in request.data and \
               len(request.data.get('users')) == 1 and \
               request.data.get('users')[0] == user.pk
