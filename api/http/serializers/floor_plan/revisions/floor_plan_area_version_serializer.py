from rest_framework import serializers
from reversion.models import Revision, Version

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.fields.json_in_string_field_serializer import JSONInStringField
from api.models import FloorPlanArea


class FloorPlanAreaVersionSerializer(BaseModelSerializer):
    class Meta:
        model = Version
        fields = ('id', 'floor_plan_area', 'serialized_data', 'revision', 'created_at', 'updated_at')

    floor_plan_area = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all(), source='object_id')
    serialized_data = JSONInStringField()
    revision = serializers.PrimaryKeyRelatedField(queryset=Revision.objects.all())
