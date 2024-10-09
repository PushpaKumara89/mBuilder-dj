from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area.floor_plan_area_serializer import FloorPlanAreaSerializer
from api.models import FloorPlanArea, FloorPlanAreaPin


class FloorPlanAreaPinSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPin
        fields = ('id', 'floor_plan_area', 'content_type', 'object_id', 'pin', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_floor_plan_area': (FloorPlanAreaSerializer, {'source': 'floor_plan_area'}),
        }

    floor_plan_area = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
    content_type = serializers.PrimaryKeyRelatedField(required=True, queryset=ContentType.objects.all())
    object_id = serializers.IntegerField(required=True, min_value=0)
    pin = serializers.JSONField(required=True)
