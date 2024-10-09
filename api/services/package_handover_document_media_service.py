from api.models import PackageHandoverDocument


class PackageHandoverDocumentMediaService:
    @classmethod
    def load_media_from_package_handover_document(cls, package_handover_document: PackageHandoverDocument, update: dict):
        return package_handover_document.packagehandoverdocumentmedia_set.filter(
            status=update.get('status')
        ).all()
