from typing import Dict, Any, Optional, Tuple
import uuid

from PIL.Image import DecompressionBombError
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from storages.base import BaseStorage

from api.models import Media, MediaThumbnail
from api.queues.media import create_thumbnails
from api.services.base_entity_service import BaseEntityService
from api.services.media_thumbnail_entity_service import MediaThumbnailEntityService
from api.services.thumbnail_service import ThumbnailService
from api.storages import AzurePrivateMediaStorage, AzurePrivateReportStorage
from mbuild.settings import IMAGE_EXTENSIONS


class MediaEntityService(BaseEntityService):
    model: Media = Media

    def create(self, validated_data: dict, create_thumbnail: bool = True) -> Media:
        sync_create_thumbnails = validated_data.pop('sync_create_thumbnails', None)
        media = self._perform_create(validated_data, 'media_private_retrieve')
        if create_thumbnail:
            if sync_create_thumbnails:
                self.create_thumbnails(media=media)
            else:
                create_thumbnails(media=media)
        return media

    def create_thumbnails(self, media: Media) -> None:
        storage = media.get_common_storage()
        file_path = storage.url(media.original_link)
        thumbnail = media
        if media.extension not in IMAGE_EXTENSIONS:
            if media.is_pdf:
                thumbnail = self.create_thumbnail_for_pdf(
                    media=media,
                    storage=storage,
                )
            elif video_stream := ThumbnailService().get_video_stream_info(file_path=file_path):
                thumbnail = self.create_thumbnail_for_video(
                    media=media,
                    file_path=file_path,
                    video_stream=video_stream,
                )

            storage = AzurePrivateMediaStorage()
        else:
            MediaThumbnailEntityService().create({
                'original_media': media,
                'thumbnail': thumbnail,
            })

        if thumbnail and thumbnail.extension in IMAGE_EXTENSIONS:
            MediaThumbnailEntityService().create_thumbnails_for_project_snapshot(
                media=media,
                storage=storage,
                thumbnail=thumbnail,
            )

    def create_thumbnail_for_pdf(self, media: Media, storage: BaseStorage,
                                 dpi: Optional[Tuple] = (MediaThumbnail.PDF_THUMBNAIL_DPI_SIZES.width,
                                                         MediaThumbnail.PDF_THUMBNAIL_DPI_SIZES.height,)
                                 ) -> Optional[Media]:
        try:
            first_pdf_page = ThumbnailService().get_pdf_first_page(media, storage, dpi)
        except DecompressionBombError:
            dpi_step = 50
            dpi = (dpi[0] - dpi_step,
                   dpi[1] - dpi_step,)

            if dpi[0] <= 0:
                return None

            return self.create_thumbnail_for_pdf(media, storage, dpi)

        if first_pdf_page is None:
            return None

        return self._create_thumbnail_for_file(media, first_pdf_page)

    def create_thumbnail_for_video(self, media: Media, file_path: str, video_stream: dict) -> Optional[Media]:
        in_memory_file = ThumbnailService().get_video_thumbnail(media=media, file_path=file_path, video_stream=video_stream)
        return self._create_thumbnail_for_file(media, in_memory_file) if in_memory_file else None

    def _create_thumbnail_for_file(self, media: Media, file: InMemoryUploadedFile) -> Media:
        image_from_file = self.create({'file': file, 'is_public': False}, create_thumbnail=False)
        MediaThumbnailEntityService().create({
            'original_media': media,
            'thumbnail': image_from_file,
        })
        return image_from_file

    def save_report(self, validated_data: Dict) -> Media:
        return self._perform_create(validated_data, 'report_private_retrieve', AzurePrivateReportStorage())

    def create_media(self, is_public: bool, original_link: str, rout_name: str, validated_data: dict, file_name: str, size: int):
        media_hash = None if is_public else uuid.uuid4().hex

        link = self._generate_link(original_link, is_public, rout_name, media_hash)

        return self.model.objects.create(name=file_name, link=link, original_link=original_link, size=size,
                                         is_public=is_public, hash=media_hash, **validated_data)

    def _perform_create(self, validated_data: Dict, rout_name: str, private_storage: Any = AzurePrivateMediaStorage()) -> Media:
        file = validated_data.pop('file')
        is_public = validated_data.pop('is_public', True)

        if settings.USE_EXTERNAL_FILES_STORAGE:
            storage = default_storage if is_public else private_storage
        else:
            storage = default_storage

        file_name = self._generate_file_name(storage, file.name)
        original_link = storage.save(file_name, file)

        return self.create_media(is_public, original_link, rout_name, validated_data, file_name, file.size)

    @staticmethod
    def _generate_link(original_link: str, is_public: bool, rout_name: str, media_hash: str) -> str:
        return original_link if is_public else settings.APP_URL + reverse(rout_name, kwargs={'uuid': media_hash})

    def create_thumbnail_media(self, resized_image_file: InMemoryUploadedFile, local_id: int | str) -> Media:
        validated_data = {'file': resized_image_file, 'is_public': False, 'local_id': local_id}
        return self.create(validated_data, create_thumbnail=False)

    def _generate_file_name(self, storage, file_name: str) -> str:
        if storage.exists(file_name):
            file_name = file_name.split('.')
            name, extension = file_name[:-1], file_name[-1]
            name.extend([str(uuid.uuid4()), extension])

            file_name = '.'.join(name)

        return file_name
