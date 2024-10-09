from rest_framework.permissions import BasePermission

from api.models import User


class AllowedToUpdateCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        def updating_user_is_company_admin(user_pk: int) -> bool:
            return User.objects.filter(groups__in=[User.Group.COMPANY_ADMIN.value], pk=user_pk).exists()

        if 'pk' in view.kwargs and updating_user_is_company_admin(view.kwargs['pk']):
            return bool(request.user) and request.user.is_company_admin

        return True
