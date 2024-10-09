from rest_framework.permissions import BasePermission


class IsConsultant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_consultant
