from rest_framework.permissions import BasePermission

from api.models import User


class AllowedToAssignCompanyAdminRole(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['update', 'partial_update', 'create']:
            if 'group' in request.data and request.data['group'] == User.Group.COMPANY_ADMIN.value:
                return request.user.is_company_admin

        return True
