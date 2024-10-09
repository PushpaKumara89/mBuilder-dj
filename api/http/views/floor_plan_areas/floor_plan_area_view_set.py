from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.floor_plan_area_filter import FloorPlanAreaFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.floor_plan_area.floor_plan_area_serializer import FloorPlanAreaSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlanArea
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager, IsProjectClient, IsProjectConsultant, IsProjectSubcontractor
from api.services.floor_plan_area_entity_service import FloorPlanAreaEntityService


class FloorPlanAreaViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
        'create': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
        'retrieve': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient
                                   | IsProjectConsultant | IsProjectSubcontractor),),
        'destroy': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    service = FloorPlanAreaEntityService()
    serializer_class = FloorPlanAreaSerializer
    filterset_class = FloorPlanAreaFilter
    queryset = FloorPlanArea.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.create(serializer.validated_data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.service.update(instance, serializer.validated_data)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.destroy(instance, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        self.queryset = self.queryset.filter(
            floor_plan__project=self.kwargs['project_pk']
        )

        return super().get_queryset()
