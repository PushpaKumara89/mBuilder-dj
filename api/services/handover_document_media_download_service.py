from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import pendulum
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import TextChoices

from api.mails.handover_document.download_multiple_handover_document_files import DownloadMultipleHandoverDocumentFiles
from api.models import Media, User, Project
from api.services.media_entity_service import MediaEntityService
from api.storages import AzurePrivateMediaStorage
from api.utilities.handover_document_utilities import extend_file_name_for_archive


class HandoverDocumentMediaDownloadService:
    class Entity(TextChoices):
        PACKAGE_HANDOVER_DOCUMENT_MEDIA = 'package_handover_document_media'
        ASSET_HANDOVER_DOCUMENT_MEDIA = 'asset_handover_document_media'

    def save_archive(self, data: dict, entity: Entity) -> Media:
        archive = self.__generate_archive(data, entity)
        filename = self.__generate_archive_name()
        uploaded_file = SimpleUploadedFile(content=archive, name=filename, content_type='application/zip')

        return MediaEntityService().create({
            'file': uploaded_file,
            'is_public': False
        }, create_thumbnail=False)

    def send_archive(self, saved_archive: Media, project_pk: int, user: User) -> None:
        # TODO move import to the module level after Handover Document Media entity remove
        from api.queues.handover_document import send_email_with_handover_document_archive

        send_email_with_handover_document_archive(saved_archive, project_pk, user)

    def send_email_with_archive(self, archive: Media, project_id: int, user: User) -> None:
        project = Project.objects.filter(id=project_id).get()
        context = {
            'link': archive.link,
            'support_email': settings.EMAIL_SUPPORT_EMAIL,
            'project_name': project.name
        }

        DownloadMultipleHandoverDocumentFiles(). \
            set_context(context). \
            set_to(user.email). \
            send()

    def __generate_archive_name(self):
        return 'handover_document_report_%s.zip' % pendulum.now().to_datetime_string()

    def __generate_archive(self, data: dict, entity: Entity) -> bytes:
        handover_documents = data[entity]
        handover_document_ids = [handover_document.media.id for handover_document in handover_documents]
        handover_document_media = Media.objects.filter(id__in=handover_document_ids).all()
        zip_file = BytesIO()
        storage = AzurePrivateMediaStorage()

        with ZipFile(zip_file, 'w', compression=ZIP_DEFLATED) as archive:
            for media in handover_document_media:
                downloaded_file = storage.open(media.original_link)
                name = self._get_file_name(media, archive)

                archive.writestr(name, downloaded_file.file.read())

        return zip_file.getvalue()

    def _get_file_name(self, media: Media, archive: ZipFile) -> str:
        name = media.name
        if name in archive.namelist():
            name = extend_file_name_for_archive(name)

        return name
