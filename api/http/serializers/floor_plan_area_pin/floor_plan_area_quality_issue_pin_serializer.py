from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan_area.floor_plan_area_serializer import FloorPlanAreaSerializer
from api.http.serializers.floor_plan_area_pin_thumbnail.floor_plan_area_pin_thumbnail_serializer import \
    FloorPlanAreaPinThumbnailSerializer
from api.models import FloorPlanArea, FloorPlanAreaPin, Subtask


class FloorPlanAreaQualityIssuePinSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanAreaPin
        fields = ('id', 'floor_plan_area', 'object_id', 'pin', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_floor_plan_area': (FloorPlanAreaSerializer, {'source': 'floor_plan_area'}),
            'expanded_quality_issue': ('api.http.serializers.quality_issue.quality_issue_serializer.QualityIssueSerializer', {'source': 'content_object'}),
            'expanded_object_id': ('api.http.serializers.quality_issue.quality_issue_serializer.QualityIssueSerializer', {'source': 'content_object'}),
            'expanded_thumbnails': (FloorPlanAreaPinThumbnailSerializer, {'source': 'floorplanareapinthumbnail_set', 'many': True}),
        }

    floor_plan_area = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlanArea.objects.all())
    object_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Subtask.objects.all())
    pin = serializers.JSONField(required=True)
