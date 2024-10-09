from rest_framework import serializers
from reversion.models import Revision

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlanRevisionMeta


class FloorPlanRevisionMetaSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlanRevisionMeta
        fields = ('id', 'event_type', 'revision', 'created_at', 'updated_at')

    event_type = serializers.CharField()
    revision = serializers.PrimaryKeyRelatedField(queryset=Revision.objects.all())
