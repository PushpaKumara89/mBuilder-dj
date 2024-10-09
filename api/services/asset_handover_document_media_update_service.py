from typing import List

from api.http.serializers import AssetHandoverDocumentMediaUpdateSerializer
from api.models import AssetHandoverDocumentMedia, AssetHandoverDocumentMediaUpdate, AssetHandoverDocument
from api.services.asset_handover_document_media_service import AssetHandoverDocumentMediaService


class AssetHandoverDocumentMediaUpdateService:
    @classmethod
    def create_bulk_updates(cls, validated_data: dict, context):
        updates = cls.form_updates_for_bulk_update(validated_data)
        serializer = AssetHandoverDocumentMediaUpdateSerializer(many=True, context=context)
        package_handover_document_media_updates = serializer.create(updates)
        cls.__remove_related_media(package_handover_document_media_updates)
        return AssetHandoverDocumentMediaUpdateSerializer(package_handover_document_media_updates, many=True).data

    @classmethod
    def form_updates_for_bulk_update(cls, validated_data: dict):
        asset_handover_document: AssetHandoverDocument = validated_data['asset_handover_document']
        asset_handover_document_media = AssetHandoverDocumentMediaService.load_media_from_asset_handover_document(
            asset_handover_document, validated_data['old_data']
        )
        return list(
            map(lambda document_media: {
                'user': validated_data['user'],
                'comment': validated_data.get('comment'),
                'old_data': validated_data['old_data'],
                'new_data': validated_data['new_data'],
                'asset_handover_document_media': document_media
            }, asset_handover_document_media)
        )

    @classmethod
    def __remove_related_media(cls, updates: List[AssetHandoverDocumentMediaUpdate]) -> None:
        asset_handover_document_media = []
        for update in updates:
            if update.new_data['status'] == AssetHandoverDocumentMedia.Status.REMOVED:
                asset_handover_document_media.append(update.asset_handover_document_media.pk)

        if asset_handover_document_media:
            AssetHandoverDocumentMedia.objects.filter(pk__in=asset_handover_document_media).delete()
