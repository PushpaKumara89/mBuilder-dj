from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area.floor_plan_area_bulk_delete_serializer import \
    FloorPlanAreaBulkDeleteSerializer
from api.http.serializers.floor_plan_area.floor_plan_area_bulk_update_serializer import \
    FloorPlanAreaBulkUpdateSerializer
from api.http.serializers.floor_plan_area.floor_plan_area_serializer import FloorPlanAreaSerializer
from api.models import FloorPlanArea


class FloorPlanAreaBulkSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanArea
        fields = ('create', 'update', 'delete',)

    create = FloorPlanAreaSerializer(many=True)
    update = FloorPlanAreaBulkUpdateSerializer(many=True, partial=True)
    delete = FloorPlanAreaBulkDeleteSerializer(many=True)
