from rest_framework.permissions import BasePermission

from api.models import Project


class IsProjectUser(BasePermission):
    def has_permission(self, request, view):
        if 'project_or_company_admins' in request.query_params:
            return Project.objects.filter(pk=int(request.query_params['project_or_company_admins']),
                                          users=request.user).exists()

        return False
