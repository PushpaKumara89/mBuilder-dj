from rest_framework import serializers

from api.http.serializers import MediaSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_serializer import FloorPlanAreaPinSerializer
from api.models import FloorPlanAreaPin, Media, FloorPlanAreaPinThumbnail


class FloorPlanAreaPinThumbnailSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPinThumbnail
        fields = ('id', 'floor_plan_area_pin', 'thumbnail', 'type', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_floor_plan_area_pin': (FloorPlanAreaPinSerializer, {'source': 'floor_plan_area_pin'}),
            'expanded_thumbnail': (MediaSerializer, {'source': 'thumbnail'}),
        }

    floor_plan_area_pin = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanAreaPin.objects.all())
    thumbnail = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all())
    type = serializers.ChoiceField(required=True, choices=FloorPlanAreaPinThumbnail.Type.choices)
