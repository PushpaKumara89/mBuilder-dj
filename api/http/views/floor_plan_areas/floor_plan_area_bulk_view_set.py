from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.floor_plan_area.floor_plan_area_bulk_serializer import FloorPlanAreaBulkSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlanArea
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager
from api.services.floor_plan_area_entity_service import FloorPlanAreaEntityService


class FloorPlanAreaBulkViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'perform_actions': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    service = FloorPlanAreaEntityService()
    serializer_class = FloorPlanAreaBulkSerializer
    queryset = FloorPlanArea.objects.all()

    def perform_actions(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.perform_actions(serializer.validated_data, request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
