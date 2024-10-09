from PIL import Image

from django.core.files.storage import default_storage
from pillow_heif import register_heif_opener

from api.utilities.image_utilities import resize_image_and_save

from api.models import Media
from api.models.media_thumbnail import MediaThumbnail


def generate_project_image_thumbnails(image_file_name: str) -> None:
    if image_file_name.lower().endswith('heic'):
        register_heif_opener()

    image = Image.open(default_storage.open(image_file_name))

    for sizes in MediaThumbnail.PROJECT_IMAGE_THUMBNAIL_SIZES:
        resize_image_and_save(image_file_name, image, sizes)


def create_thumbnails(media: Media) -> None:
    from api.services.media_entity_service import MediaEntityService

    MediaEntityService().create_thumbnails(media=media)
