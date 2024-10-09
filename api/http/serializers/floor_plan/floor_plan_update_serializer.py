from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import FloorPlan, Package, Media, LocationMatrixPackage


class FloorPlanUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = FloorPlan
        fields = ('id', 'project', 'package', 'building', 'level', 'media', 'created_at', 'updated_at', 'keep_floor_plan_areas_and_floor_plan_pins')

    project = serializers.PrimaryKeyRelatedField(read_only=True)
    package = serializers.PrimaryKeyRelatedField(required=True, queryset=Package.objects.all())
    media = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all())
    building = serializers.CharField(required=True, max_length=255)
    level = serializers.CharField(required=True, max_length=255)
    keep_floor_plan_areas_and_floor_plan_pins = serializers.BooleanField(write_only=True, default=False)

    def validate(self, attrs):
        if 'package' in attrs:
            def is_package_not_related_to_project():
                return not LocationMatrixPackage.objects.filter(enabled=True, package_matrix__project_id=self.instance.project_id,
                                                                package_id=attrs['package'].pk).exists()

            if is_package_not_related_to_project():
                raise ValidationError({'package': _('Package should be from the project %s.' % self.instance.project.name)})

        return attrs
