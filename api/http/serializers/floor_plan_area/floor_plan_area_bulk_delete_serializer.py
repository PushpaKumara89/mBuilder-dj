from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlanArea


class FloorPlanAreaBulkDeleteSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanArea
        fields = ('id',)

    id = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
