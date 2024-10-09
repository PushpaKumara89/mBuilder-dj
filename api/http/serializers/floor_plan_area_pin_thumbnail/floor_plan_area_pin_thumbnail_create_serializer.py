from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlanAreaPinThumbnail, FloorPlan, FloorPlanArea


class FloorPlanAreaPinThumbnailCreateSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPinThumbnail
        fields = ('id', 'floor_plan', 'pin_coordinates', 'floor_plan_area', 'type', 'created_at', 'updated_at')

    floor_plan = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlan.objects.all())
    pin_coordinates = serializers.JSONField(required=True)
    floor_plan_area = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
    type = serializers.ListField(child=serializers.ChoiceField(required=True, choices=FloorPlanAreaPinThumbnail.Type.choices), required=True)
