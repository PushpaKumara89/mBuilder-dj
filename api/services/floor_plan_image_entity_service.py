from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from api.models import Media
from api.models.base_model import BaseModel
from api.models.floor_plan_image import FloorPlanImage
from api.services.base_entity_service import BaseEntityService
from api.services.media_entity_service import MediaEntityService
from api.utilities.pdf_utilities import convert_pdf_page_to_image


class FloorPlanImageEntityService(BaseEntityService):
    model: FloorPlanImage = FloorPlanImage

    def create(self, validated_data: dict, **kwargs) -> BaseModel:
        media = validated_data['media']
        storage = media.get_common_storage()

        bytes_input = convert_pdf_page_to_image(page_number=1,
                                                pdf_data=BytesIO(storage.open(media.name).file.read()),
                                                image_options={'dpi': (FloorPlanImage.DPI_SIZES.width,
                                                                       FloorPlanImage.DPI_SIZES.height),
                                                               'alpha_layer': 255})

        converted_image = self._get_in_memory_file(media=media, bytes_input=bytes_input)
        image = MediaEntityService().create(validated_data={'file': converted_image}, create_thumbnail=False)

        return super().create(validated_data={'plan_id': media.id, 'image_id': image.id})

    def _get_in_memory_file(self, media: Media, bytes_input: BytesIO) -> InMemoryUploadedFile:
        name = '.'.join(media.original_link.split('.')[0:-1])
        return InMemoryUploadedFile(file=bytes_input, field_name=None, name=f'{name}.png',
                                    content_type='image/png', size=bytes_input.getbuffer().nbytes, charset=None)
