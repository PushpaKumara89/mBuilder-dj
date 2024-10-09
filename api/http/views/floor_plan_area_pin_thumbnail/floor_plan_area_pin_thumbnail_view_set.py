from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.floor_plan_area_pin_thumbnail.floor_plan_area_pin_thumbnail_create_serializer import \
    FloorPlanAreaPinThumbnailCreateSerializer
from api.http.serializers.media.media_pi_thumbnail_serializer import MediaPinThumbnailSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlanAreaPinThumbnail, Project, FloorPlan
from api.permissions import IsSuperuser, IsProjectUser
from api.services.floor_plan_area_pin_thumbnail_entity_service import FloorPlanAreaPinThumbnailEntityService


class FloorPlanAreaPinThumbnailViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'create': (IsAuthenticated, (IsSuperuser | IsProjectUser),),
    }

    service = FloorPlanAreaPinThumbnailEntityService()
    serializer_class = FloorPlanAreaPinThumbnailCreateSerializer
    queryset = FloorPlanAreaPinThumbnail.objects.all()

    def create(self, request, *args, **kwargs):
        get_object_or_404(queryset=Project.objects.all(), pk=kwargs['project_pk'])
        floor_plan = get_object_or_404(queryset=FloorPlan.objects.all(), pk=kwargs['pk'])
        request.data['floor_plan'] = floor_plan.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = self.service.create_temporary_pin_thumbnail(serializer.validated_data)

        headers = self.get_success_headers(images)
        return Response(MediaPinThumbnailSerializer(images, many=True).data, status=status.HTTP_201_CREATED, headers=headers)
