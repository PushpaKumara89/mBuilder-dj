from datetime import datetime

from mbuild.settings import app as celery_app

from api.models import User, HandoverDocumentArchivePart


@celery_app.task(queue='handover_document_archive', time_limit=3600)
def initiate_generation_process(project: int, user: User, generation_started_at: datetime) -> None:
    from api.services.handover_document_archive_service import HandoverDocumentArchiveService

    HandoverDocumentArchiveService().initiate_generation_process(project, user, generation_started_at)


@celery_app.task(queue='handover_document_archive', time_limit=72000)
def generate_archive_part(archive_part: HandoverDocumentArchivePart) -> None:
    from api.services.handover_document_archive_service import HandoverDocumentArchiveService

    HandoverDocumentArchiveService().create_archive_part_file(archive_part)
