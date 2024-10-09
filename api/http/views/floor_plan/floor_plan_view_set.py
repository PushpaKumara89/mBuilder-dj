from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.floor_plan.floor_plan_filter import FloorPlanFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import FloorPlanSerializer, FloorPlanUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlan, Project
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager, IsProjectUser
from api.services.floor_plan_entity_service import FloorPlanEntityService


class FloorPlanViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
        'create': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
        'retrieve': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectUser),),
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectUser),),
        'destroy': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    serializer_class = FloorPlanSerializer
    queryset = FloorPlan.objects.all()
    filterset_class = FloorPlanFilter

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(project=self.kwargs['project_pk'])

        return self.queryset

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs['project_pk'])
        request.data['project'] = project.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        FloorPlanEntityService().create_or_update(serializer.validated_data, request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = FloorPlanUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        FloorPlanEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
