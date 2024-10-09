from io import BytesIO

from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.models.media_thumbnail import ThumbnailSizes


def resize_image_and_save(image_file_name, image, sizes: ThumbnailSizes) -> None:
    b = BytesIO()

    copied_image = image.convert('RGB').copy()
    copied_image.thumbnail((sizes.width * 2, sizes.height * 2), Image.ANTIALIAS)
    copied_image.save(b, format='JPEG', quality='maximum', optimize=True, progressive=True)

    resized_image_file = InMemoryUploadedFile(b, None, 'temp.jpg', 'image/jpeg', b.getbuffer().nbytes, None)

    new_filename = generate_image_name_by_size(image_file_name, sizes)
    default_storage.save(new_filename, resized_image_file)


def generate_image_name_by_size(name, sizes: ThumbnailSizes):
    return '%sx%s_%s' % (sizes.width, sizes.height, name)

