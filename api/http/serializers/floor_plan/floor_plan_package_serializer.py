from api.http.serializers import PackageSerializer, MediaSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlan


class FloorPlanPackageSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlan
        fields = ('package', 'media',)

    package = PackageSerializer()
    media = MediaSerializer()
