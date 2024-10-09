from rest_framework import fields, serializers

from api.http.serializers.package_matrix.package_matrix_serializer import PackageMatrixSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageMatrix
from api.models.package_handover.package_handover import PackageHandover
from api.http.serializers.package_activity.package_activity_short_serializer import PackageActivityShortSerializer


class PackageHandoverSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandover
        fields = ('id', 'inspection_period', 'maintenance_period', 'package_matrix',)
        expandable_fields = {
            'expanded_package_matrix': (PackageMatrixSerializer, {'source': 'package_matrix'}),
            'expanded_package_activity': (PackageActivityShortSerializer, {'source': 'package_matrix.package_activity'})
        }

    inspection_period = fields.ChoiceField(choices=PackageHandover.InspectionPeriod.choices, allow_null=True, required=False)
    maintenance_period = fields.ChoiceField(choices=PackageHandover.MaintenancePeriod.choices, allow_null=True, required=False)
    package_matrix = serializers.PrimaryKeyRelatedField(queryset=PackageMatrix.objects.all(), required=True)
