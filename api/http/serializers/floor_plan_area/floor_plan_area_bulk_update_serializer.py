from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlan, FloorPlanArea


class FloorPlanAreaBulkUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanArea
        fields = ('id', 'floor_plan', 'polygon', 'area',)

    id = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
    floor_plan = serializers.PrimaryKeyRelatedField(required=False, queryset=FloorPlan.objects.all())
    area = serializers.CharField(required=False, max_length=255)
    polygon = serializers.JSONField(required=False)
