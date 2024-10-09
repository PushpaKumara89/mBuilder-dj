from rest_framework import serializers

from api.http.serializers import UserSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.floor_plan.revisions.floor_plan_area_version_serializer import FloorPlanAreaVersionSerializer
from api.http.serializers.floor_plan.revisions.floor_plan_revision_meta_serializer import FloorPlanRevisionMetaSerializer
from api.http.serializers.floor_plan.revisions.floor_plan_version_serializer import FloorPlanVersionSerializer
from api.models import User
from api.models.floor_plan_revision import FloorPlanRevision


class FloorPlanRevisionSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanRevision
        fields = ('id', 'user', 'created_at')
        expandable_fields = {
            'expanded_meta': (FloorPlanRevisionMetaSerializer, {'source': 'floorplanrevisionmeta_set', 'many': True}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_floor_plan': (FloorPlanVersionSerializer, {'source': 'floor_plan'}),
            'expanded_floor_plan_areas': (FloorPlanAreaVersionSerializer, {'source': 'floor_plan_areas', 'many': True}),
        }

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created_at = serializers.DateTimeField(source='date_created')
