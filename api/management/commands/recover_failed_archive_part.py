from django.core.management.base import BaseCommand

from api.models import HandoverDocumentArchivePart
from api.queues.celery.handover_document_archive import generate_archive_part
from api.services.handover_document_archive_part_entity_service import HandoverDocumentArchivePartEntityService


class Command(BaseCommand):
    help = "Recover failed handover document archive parts."

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Recover all archive parts.')
        parser.add_argument('archive_part', help='Recover specific archive part.', type=int, nargs='?', default=None)

    def handle(self, *args, **options):
        all_ = options['all']
        archive_part = options['archive_part']

        if not (all_ or archive_part):
            self.stdout.write(self.style.WARNING('You should specify at least one argument.'))
            return

        if archive_part and all_:
            self.stdout.write(self.style.WARNING('You should specify only one argument.'))
            return

        if archive_part:
            archive_part: HandoverDocumentArchivePart = HandoverDocumentArchivePart.objects.filter(
                id=archive_part).first()

            if not archive_part:
                self.stdout.write(self.style.WARNING('Archive part doesn\'t exist.'))
                return

            if not archive_part.is_failed:
                self.stdout.write(self.style.WARNING('Specified archive part doesn\'t failed.'))
                return

            archive_part = HandoverDocumentArchivePartEntityService().update(
                archive_part, {'status': HandoverDocumentArchivePart.Status.WAITING, 'error_track_id': None}
            )

            generate_archive_part.delay(archive_part)

            self.stdout.write(self.style.WARNING('Archive part recovered.'))
        elif all_:
            queryset = HandoverDocumentArchivePart.objects.filter(
                status=HandoverDocumentArchivePart.Status.FAILED
            )

            handover_document_parts = list(queryset)

            queryset.update(status=HandoverDocumentArchivePart.Status.WAITING, error_track_id=None)

            for handover_document_part in handover_document_parts:
                generate_archive_part.delay(handover_document_part)

            self.stdout.write(self.style.WARNING('All failed archive parts recovered.'))
