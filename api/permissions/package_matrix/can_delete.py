from rest_framework.permissions import BasePermission

from api.models import PackageMatrix


class CanDelete(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return PackageMatrix.objects.filter(pk=view.kwargs['pk'],
                                            project__users__pk=user.pk,
                                            project__users__is_staff=True).exists()
