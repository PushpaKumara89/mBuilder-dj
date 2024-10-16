from api.http.serializers import PackageHandoverDocumentMediaUpdateSerializer
from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_list_serializer import \
    PackageHandoverDocumentMediaUpdateListSerializer


class PackageHandoverDocumentMediaUploadUpdateSerializer(PackageHandoverDocumentMediaUpdateSerializer):
    class Meta(PackageHandoverDocumentMediaUpdateSerializer.Meta):
        list_serializer_class = PackageHandoverDocumentMediaUpdateListSerializer
