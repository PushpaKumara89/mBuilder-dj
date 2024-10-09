from rest_framework.permissions import BasePermission

from api.models import Project


class DoesProjectHasUsersFromSameCompany(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return Project.objects.filter(pk=view.kwargs['pk'], users__company=user.company).exists()
