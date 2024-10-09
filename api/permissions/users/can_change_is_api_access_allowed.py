from rest_framework.permissions import BasePermission


class CanChangeIsApiAccessAllowed(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_company_admin \
            if 'is_api_access_allowed' in request.data \
            else True
