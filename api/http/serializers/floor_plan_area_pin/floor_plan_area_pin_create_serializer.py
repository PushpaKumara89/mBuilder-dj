from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlanArea, FloorPlanAreaPin


class FloorPlanAreaPinCreateSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPin
        fields = ('id', 'floor_plan_area', 'object_id', 'pin', 'created_at', 'updated_at')

    floor_plan_area = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
    object_id = serializers.IntegerField(required=False, min_value=1)
    pin = serializers.JSONField(required=True)
