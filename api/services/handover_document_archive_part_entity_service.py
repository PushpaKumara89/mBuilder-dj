from api.models import HandoverDocumentArchivePart

from api.services.base_entity_service import BaseEntityService


class HandoverDocumentArchivePartEntityService(BaseEntityService):
    model: HandoverDocumentArchivePart = HandoverDocumentArchivePart

    def set_status_to_running(self, archive_part: HandoverDocumentArchivePart):
        self.update(archive_part, {'status': HandoverDocumentArchivePart.Status.RUNNING})

    def set_status_to_sent(self, archive_part: HandoverDocumentArchivePart):
        self.update(archive_part, {'status': HandoverDocumentArchivePart.Status.SENT})

    def set_status_to_saved(self, archive_part: HandoverDocumentArchivePart):
        self.update(archive_part, {'status': HandoverDocumentArchivePart.Status.SAVED})

    def mark_as_failed(self, archive_part: HandoverDocumentArchivePart, error_track_id: str):
        self.update(archive_part, {'status': HandoverDocumentArchivePart.Status.FAILED,
                                   'error_track_id': error_track_id})
