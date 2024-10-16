from api.http.serializers import AssetHandoverDocumentMediaUpdateSerializer
from api.http.serializers.asset_handover.asset_handover_document_media_update.asset_handover_document_media_update_list_serializer import \
    AssetHandoverDocumentMediaUpdateListSerializer


class AssetHandoverDocumentMediaUploadUpdateSerializer(AssetHandoverDocumentMediaUpdateSerializer):
    class Meta(AssetHandoverDocumentMediaUpdateSerializer.Meta):
        list_serializer_class = AssetHandoverDocumentMediaUpdateListSerializer
