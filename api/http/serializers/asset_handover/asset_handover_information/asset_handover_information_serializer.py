from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.http.serializers.asset_handover.asset_handover_information.asset_handover_information_editable_data_serializer import \
    AssetHandoverInformationEditableDataSerializer
from api.models import AssetHandover, AssetHandoverInformation


class AssetHandoverInformationSerializer(AssetHandoverInformationEditableDataSerializer):
    class Meta(AssetHandoverInformationEditableDataSerializer.Meta):
        fields = AssetHandoverInformationEditableDataSerializer.Meta.fields + ('asset_handover',)

    asset_handover = serializers.PrimaryKeyRelatedField(required=True, queryset=AssetHandover.objects.all(),
                                                        validators=[
                                                            UniqueValidator(
                                                                queryset=AssetHandoverInformation.objects.all())
                                                        ])
