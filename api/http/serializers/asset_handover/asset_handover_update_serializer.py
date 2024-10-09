from rest_framework import serializers

from api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_serializer import AssetHandoverDocumentSerializer
from api.http.serializers.asset_handover.asset_handover_information.asset_handover_information_serializer import \
    AssetHandoverInformationSerializer
from api.http.serializers.asset_handover.asset_handover_information.asset_handover_information_editable_data_serializer import \
    AssetHandoverInformationEditableDataSerializer
from api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_editable_data_serializer import \
    AssetHandoverDocumentEditableDataSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandover, PackageActivity, AssetHandoverDocument, AssetHandoverInformation


class AssetHandoverUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandover
        fields = ('id', 'package_activity', 'documents',
                  'asset_handover_information', 'created_at', 'updated_at',)

    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=True)
    documents = AssetHandoverDocumentEditableDataSerializer(many=True, required=True)
    asset_handover_information = AssetHandoverInformationEditableDataSerializer(required=False)

    def update(self, instance, validated_data):
        self.__update_asset_handover_documents()
        self.__update_asset_handover_information()

    def __update_asset_handover_documents(self):
        if 'documents' in self.validated_data:
            for document in self.validated_data['documents']:
                if 'number_required_files' not in document:
                    document['number_required_files'] = 0

                document_instance = AssetHandoverDocument.objects.filter(
                    asset_handover_id=self.instance.pk, document_type_id=document['document_type'].pk
                ).get()

                AssetHandoverDocumentSerializer().update(document_instance, document)

    def __update_asset_handover_information(self):
        if 'asset_handover_information' in self.validated_data:
            asset_handover_information = AssetHandoverInformation.objects.filter(
                asset_handover_id=self.instance.pk).first()

            if asset_handover_information:
                AssetHandoverInformationSerializer().update(asset_handover_information,
                                                            self.validated_data['asset_handover_information'])
            else:
                asset_handover_information = self.validated_data['asset_handover_information']
                asset_handover_information['asset_handover'] = self.instance
                AssetHandoverInformationSerializer().create(asset_handover_information)
