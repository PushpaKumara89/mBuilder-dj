from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.task_update_filter import TaskUpdateFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import TaskUpdateBulkCreateSerializer
from api.http.serializers.task_update.task_update_serializer import TaskUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import TaskUpdate
from api.permissions import IsSuperuser
from api.permissions import IsProjectStaff
from rest_framework import mixins, status

from api.permissions.permission_group import PermissionGroup
from api.services.task_update_entity_service import TaskUpdateEntityService


class TaskUpdateViewSet(BaseViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, ListModelMixin):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'create': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'bulk_create': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
    }
    serializer_class = TaskUpdateSerializer
    service = TaskUpdateEntityService()
    filterset_class = TaskUpdateFilter
    queryset = TaskUpdate.objects.all()

    def get_queryset(self):
        if 'task_pk' in self.kwargs:
            return super().get_queryset().filter(task__pk=self.kwargs['task_pk'])

        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['task'] = kwargs['task_pk']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.create(serializer.validated_data)

        return Response(data=self.get_serializer(result).data, status=status.HTTP_201_CREATED)

    def bulk_create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk

        serializer = TaskUpdateBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.bulk_create(serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)
