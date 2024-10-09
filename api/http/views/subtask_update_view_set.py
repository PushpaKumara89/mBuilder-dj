from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.subtask_update_filter import SubtaskUpdateFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import SubtaskUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import SubtaskUpdate
from api.permissions import IsProjectStaff, IsSuperuser
from api.permissions.permission_group import PermissionGroup
from api.permissions.subtask_updates import CanSubcontractorChangeStatus, IsSubtaskSubcontractor
from api.services.subtask_update_entity_service import SubtaskUpdateEntityService


class SubtaskUpdateViewSet(BaseViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, ListModelMixin):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsSubtaskSubcontractor, ),),
        'create': (IsAuthenticated, IsSuperuser | IsProjectStaff | CanSubcontractorChangeStatus,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsSubtaskSubcontractor, ),),
    }
    serializer_class = SubtaskUpdateSerializer
    service = SubtaskUpdateEntityService()
    filterset_class = SubtaskUpdateFilter
    queryset = SubtaskUpdate.objects.all()

    def get_queryset(self):
        if 'subtask_pk' in self.kwargs:
            return super().get_queryset().filter(subtask__pk=self.kwargs['subtask_pk'])

        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['subtask'] = kwargs['subtask_pk']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.create(
            validated_data=serializer.validated_data,
            user=request.user,
            project_pk=kwargs['project_pk']
        )

        return Response(data=self.get_serializer(result).data, status=status.HTTP_201_CREATED)
