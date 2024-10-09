from rest_framework.permissions import BasePermission

from api.models import AppSettings


class AllowedRegistrationUser(BasePermission):
    def has_permission(self, request, view):
        return not AppSettings.objects.filter(disable_user_registration_from_mobile_devices=True).exists()
