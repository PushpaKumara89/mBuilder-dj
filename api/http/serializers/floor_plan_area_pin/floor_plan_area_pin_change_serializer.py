from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlanArea, FloorPlanAreaPin


class FloorPlanAreaPinChangeSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPin
        fields = ('id', 'floor_plan_area', 'object_id', 'pin', 'created_at', 'updated_at')

    floor_plan_area = serializers.PrimaryKeyRelatedField(required=False, queryset=FloorPlanArea.objects.all())
    object_id = serializers.IntegerField(required=False)
    pin = serializers.JSONField(required=False)
