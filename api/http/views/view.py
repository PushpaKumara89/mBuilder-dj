from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from api.http.pagination import PageNumberPagination
from api.permissions.permission_group import PermissionGroup
from api.utilities.helpers import get_boolean_query_param


class BaseViewSet(viewsets.GenericViewSet):
    _request_permissions = []
    service_class = None
    pagination_class = PageNumberPagination
    limit_offset_pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)

    def get_serializer(self, *args, **kwargs):
        is_update = self.request.method == 'PUT'
        request_context = {'request': self.request, **self.get_serializer_context()}

        if 'project_pk' in self.kwargs:
            request_context['project_pk'] = self.kwargs['project_pk']

        kwargs['partial'] = is_update
        kwargs['context'] = {**kwargs['context'], **request_context} if 'context' in kwargs else request_context

        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        try:
            self.permission_classes = self._request_permissions[self.action]

            return super().get_permissions()
        except BaseException as e:
            raise PermissionDenied()

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if isinstance(permission, PermissionGroup):
                permission.has_permission(request, self)
            else:
                if not permission.has_permission(request, self):
                    self.permission_denied(
                        request,
                        message=getattr(permission, 'message', None),
                        code=getattr(permission, 'code', None)
                    )

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if isinstance(permission, PermissionGroup):
                permission.has_object_permission(request, self, obj)
            else:
                if not permission.has_object_permission(request, self, obj):
                    self.permission_denied(
                        request,
                        message=getattr(permission, 'message', None),
                        code=getattr(permission, 'code', None)
                    )

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                pagination_class = self.limit_offset_pagination_class \
                    if get_boolean_query_param(self.request.query_params, 'use_limit_offset_pagination') \
                    else self.pagination_class
                self._paginator = pagination_class()

        return self._paginator
