import json

from rest_framework import serializers
from reversion.models import Revision, Version

from api.http.serializers import MediaSerializer, PackageSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.fields.json_in_string_field_serializer import JSONInStringField
from api.models import FloorPlan, Media, Package


class FloorPlanVersionSerializer(BaseModelSerializer):
    class Meta:
        model = Version
        fields = ('id', 'floor_plan', 'serialized_data', 'revision', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_media': (serializers.SerializerMethodField, {'method_name': 'get_media'}),
            'expanded_image': (serializers.SerializerMethodField, {'method_name': 'get_image'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'get_package'})
        }

    floor_plan = serializers.PrimaryKeyRelatedField(required=True, queryset=FloorPlan.objects.all(), source='object_id')
    serialized_data = JSONInStringField()
    revision = serializers.PrimaryKeyRelatedField(queryset=Revision.objects.all())

    def get_media(self, obj: Version):
        deserialized_data = json.loads(obj.serialized_data)
        floor_plan_data = deserialized_data[0]['fields']
        media = Media.objects.get(id=floor_plan_data['media'])
        return MediaSerializer(media).data

    def get_image(self, obj: Version):
        deserialized_data = json.loads(obj.serialized_data)
        floor_plan_media = Media.objects.prefetch_related('floor_plan_image').get(pk=deserialized_data[0]['fields']['media'])
        floor_plan_image = floor_plan_media.floorplanimage_set.first()

        if not floor_plan_image:
            return None

        return MediaSerializer(floor_plan_image.image).data

    def get_package(self, obj: Version):
        deserialized_data = json.loads(obj.serialized_data)
        floor_plan_data = deserialized_data[0]['fields']
        media = Package.objects.get(id=floor_plan_data['package'])
        return PackageSerializer(media).data
