from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan.floor_plan_serializer import FloorPlanSerializer
from api.http.validators import UniqueTogetherValidator
from api.models import FloorPlan, FloorPlanArea


class FloorPlanAreaSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanArea
        validators = [
            UniqueTogetherValidator(
                fields=['floor_plan', 'area'], queryset=FloorPlanArea.objects.all()
            )
        ]
        fields = ('id', 'floor_plan', 'polygon', 'area', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_floor_plan': (FloorPlanSerializer, {'source': 'floor_plan'}),
        }

    floor_plan = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlan.objects.all())
    area = serializers.CharField(required=True, max_length=255)
    polygon = serializers.JSONField(required=True)
