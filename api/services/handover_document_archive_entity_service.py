from api.models import HandoverDocumentArchive
from api.services.base_entity_service import BaseEntityService


class HandoverDocumentArchiveEntityService(BaseEntityService):
    model: HandoverDocumentArchive = HandoverDocumentArchive

    def set_status_to_completed(self, entity: HandoverDocumentArchive) -> None:
        self.update(entity, {'status': HandoverDocumentArchive.Status.COMPLETED})
