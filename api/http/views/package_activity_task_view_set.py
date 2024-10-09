from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.package_activity_task_filter import PackageActivityTaskFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.http.serializers.package_matrix_hidden_activity_task_serializer import \
    PackageMatrixHiddenActivityTaskSerializer
from api.http.views.view import BaseViewSet
from api.models import PackageActivityTask
from api.permissions import IsSuperuser
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup
from api.services.package_activity_task_entity_service import PackageActivityTaskEntityService


class PackageActivityTaskViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'update': (IsAuthenticated, IsSuperuser,),
        'hide': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'show': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
    }

    serializer_class = PackageActivityTaskSerializer
    queryset = PackageActivityTask.objects.all()
    filterset_class = PackageActivityTaskFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PackageActivityTaskEntityService().create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        PackageActivityTaskEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def hide(self, request, *args, **kwargs):
        package_matrix = kwargs.get('package_matrix_pk', None)
        activity_task = kwargs.get('task_pk', None)
        data = {'package_activity_task': activity_task, 'package_matrix': package_matrix}

        serializer = PackageMatrixHiddenActivityTaskSerializer(data=data, action=PackageMatrixHiddenActivityTaskSerializer.Action.HIDE)
        serializer.is_valid(raise_exception=True)
        PackageActivityTaskEntityService().hide_package_matrix_task(serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    def show(self, request, *args, **kwargs):
        package_matrix = kwargs.get('package_matrix_pk')
        activity_task = kwargs.get('task_pk')
        data = {'package_activity_task': activity_task, 'package_matrix': package_matrix}

        serializer = PackageMatrixHiddenActivityTaskSerializer(data=data, action=PackageMatrixHiddenActivityTaskSerializer.Action.SHOW)
        serializer.is_valid(raise_exception=True)
        PackageActivityTaskEntityService().show_package_matrix_task(serializer.data, request.user, kwargs.get('project_pk'))

        return Response(status=status.HTTP_200_OK)
