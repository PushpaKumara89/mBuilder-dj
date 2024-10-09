from rest_framework.permissions import BasePermission


class NotAllowAny(BasePermission):

    def has_permission(self, request, view):
        return False
