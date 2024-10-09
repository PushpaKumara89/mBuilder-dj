import dataclasses
from io import BytesIO
from typing import Iterator

import PIL
from PIL import Image, ImageFile
from PIL.Image import DecompressionBombError
from django.core.files.uploadedfile import InMemoryUploadedFile
from pillow_heif import register_heif_opener
from sentry_sdk import capture_exception
from storages.base import BaseStorage
from wand.image import Image as WandImage

from api.models import Media
from api.models.media_thumbnail import MediaThumbnail, ThumbnailSizes
from api.services.base_entity_service import BaseEntityService


ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclasses.dataclass(frozen=True)
class ThumbnailMedia:
    media: Media
    width: int
    height: int


class MediaThumbnailEntityService(BaseEntityService):
    model: MediaThumbnail = MediaThumbnail

    def create_thumbnails_for_project_snapshot(
            self,
            media: Media,
            thumbnail: Media,
            storage: BaseStorage,
    ) -> None:
        thumbnails = self.get_thumbnails_if_not_exists(media=media, thumbnail=thumbnail, storage=storage,
                                                       sizes=MediaThumbnail.PROJECT_SNAPSHOT_THUMBNAIL_SIZES)
        for thumbnail in thumbnails:
            self.create({
                'original_media': media,
                'thumbnail': thumbnail.media,
                'width': thumbnail.width,
                'height': thumbnail.height,
            })

    def get_thumbnails_if_not_exists(self, media: Media, thumbnail: Media, storage: BaseStorage, sizes: list[ThumbnailSizes]) -> \
            Iterator[ThumbnailMedia]:
        """
            Generates and yields thumbnail images of different sizes for a given media item if they do not already exist.

            This function opens the original thumbnail image, resizes it according to the dimensions specified in the sizes
            parameter, and creates new thumbnail media objects if they do not exist in the database.

            :param media: A Media object representing the original media item.
            :param thumbnail: A Media object representing the original thumbnail image.
            :param storage: A BaseStorage object to interact with the storage backend.
            :param sizes: A list of ThumbnailSizes objects containing the dimensions for the thumbnail images to be created.
            :return: An iterator yielding ThumbnailMedia objects containing the created thumbnail media and dimensions.
            """
        from api.services.media_entity_service import MediaEntityService

        with storage.open(thumbnail.original_link) as image_file:
            if thumbnail.original_link.lower().endswith('heic'):
                register_heif_opener()
            elif thumbnail.original_link.lower().endswith('svg'):
                with WandImage(file=image_file) as svg_file, svg_file.convert('png') as converted_file:
                    image_file = BytesIO()
                    converted_file.save(file=image_file)

            try:
                image = Image.open(image_file)
            except DecompressionBombError:
                PIL.Image.MAX_IMAGE_PIXELS = None
                image = Image.open(image_file)
            except Exception as e:
                capture_exception(e)
                return []

            for size in sizes:
                resized_image_file = self._create_resized_in_memory_image(image, size, thumbnail)
                thumbnail_exists = self.model.objects.filter(
                    original_media=media,
                    thumbnail__name=resized_image_file.name,
                ).exists()
                if not thumbnail_exists:
                    thumbnail = MediaEntityService().create_thumbnail_media(resized_image_file, media.local_id)
                    yield ThumbnailMedia(media=thumbnail, width=size.width, height=size.height)

    def _create_resized_in_memory_image(self, image: Image, sizes: ThumbnailSizes, media: Media) -> InMemoryUploadedFile:
        if media.extension in ('jpeg', 'jpg'):
            extension = 'jpeg'
            pil_format = 'JPEG'
            file_content_type = 'image/jpeg'
        else:
            extension = 'png'
            pil_format = 'PNG'
            file_content_type = 'image/png'

        b = BytesIO()

        copied_image = image.copy()
        copied_image = copied_image.convert('RGB')
        copied_image.thumbnail((sizes.width, sizes.height), Image.ANTIALIAS)
        copied_image.save(b, format=pil_format, quality='maximum', optimize=True, progressive=True)

        new_filename = self._generate_image_name_by_size(media.name, sizes)
        return InMemoryUploadedFile(b, None, f'{new_filename}.{extension}', file_content_type, b.getbuffer().nbytes, None)

    def _generate_image_name_by_size(self, name: str, sizes: ThumbnailSizes) -> str:
        return f'{sizes.width}x{sizes.height}_{name}'
