from rest_framework.permissions import BasePermissionMetaclass


class PermissionGroup(metaclass=BasePermissionMetaclass):
    permissions_classes: list = list()
    permissions: list

    def __init__(self, *permissions):
        self.permissions_classes = list(permissions)

    def has_permission(self, request, view):
        for permission in self.permissions:
            if not permission.has_permission(request, view):
                view.permission_denied(
                    request,
                    message=getattr(permission, 'message', None),
                    code=getattr(permission, 'code', None)
                )
        return True

    def has_object_permission(self, request, view, obj):
        for permission in self.permissions:
            if not permission.has_object_permission(request, self, obj):
                view.permission_denied(
                    request,
                    message=getattr(permission, 'message', None),
                    code=getattr(permission, 'code', None)
                )
        return True

    def __call__(self, *args, **kwargs):
        self.permissions = list(permissions_class() for permissions_class in self.permissions_classes)
        return self
