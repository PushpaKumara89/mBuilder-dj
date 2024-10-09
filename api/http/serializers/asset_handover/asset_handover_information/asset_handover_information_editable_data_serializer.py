from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverInformation


class AssetHandoverInformationEditableDataSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverInformation
        fields = ('id', 'guid_external_ref', 'warranty', 'manufacture_serial_number',
                  'model_number', 'created_at', 'updated_at',)

    guid_external_ref = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    warranty = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    manufacture_serial_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    model_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
