from typing import List

from api.http.serializers import PackageHandoverDocumentMediaUpdateSerializer
from api.models import PackageHandoverDocument, PackageHandoverDocumentMediaUpdate, PackageHandoverDocumentMedia
from api.services.package_handover_document_media_service import PackageHandoverDocumentMediaService


class PackageHandoverDocumentMediaUpdateService:
    @classmethod
    def create_bulk_updates(cls, validated_data: dict, context):
        updates = cls.form_updates_for_bulk_update(validated_data)
        serializer = PackageHandoverDocumentMediaUpdateSerializer(many=True, context=context)
        package_handover_document_media_updates = serializer.create(updates)
        cls.__remove_related_media(package_handover_document_media_updates)
        return PackageHandoverDocumentMediaUpdateSerializer(package_handover_document_media_updates, many=True).data

    @classmethod
    def form_updates_for_bulk_update(cls, validated_data: dict):
        package_handover_document: PackageHandoverDocument = validated_data['package_handover_document']
        package_handover_document_media = PackageHandoverDocumentMediaService.load_media_from_package_handover_document(
            package_handover_document, validated_data['old_data']
        )
        return list(
            map(lambda document_media: {
                'user': validated_data['user'],
                'comment': validated_data.get('comment'),
                'old_data': validated_data['old_data'],
                'new_data': validated_data['new_data'],
                'package_handover_document_media': document_media
            }, package_handover_document_media)
        )

    @classmethod
    def __remove_related_media(cls, updates: List[PackageHandoverDocumentMediaUpdate]) -> None:
        package_handover_document_media = []
        for update in updates:
            if update.new_data['status'] == PackageHandoverDocumentMedia.Status.REMOVED:
                package_handover_document_media.append(update.package_handover_document_media.pk)

        if package_handover_document_media:
            PackageHandoverDocumentMedia.objects.filter(pk__in=package_handover_document_media).delete()
