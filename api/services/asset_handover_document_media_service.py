from api.models import AssetHandoverDocument


class AssetHandoverDocumentMediaService:
    @classmethod
    def load_media_from_asset_handover_document(cls, asset_handover_document: AssetHandoverDocument, update: dict):
        return asset_handover_document.assethandoverdocumentmedia_set.filter(
            status=update.get('status')
        ).all()
