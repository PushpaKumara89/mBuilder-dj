from rest_framework.permissions import BasePermission

from api.models import Project


class CanManage(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return Project.objects.filter(users__pk=user.pk,
                                      projectnews__pk=view.kwargs.get('pk'),
                                      users__is_staff=True).exists()
