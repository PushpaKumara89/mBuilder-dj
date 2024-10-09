from rest_framework.permissions import BasePermission

from api.models import LocationMatrix


class IsLocationMatrixProjectStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return LocationMatrix.objects.filter(pk=view.kwargs.get('pk'), project__users=user, project__users__is_staff=True).exists()
