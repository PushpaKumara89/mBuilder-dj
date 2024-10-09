import gc
import io
import operator

from PIL import Image, ImageDraw, ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import FloorPlanAreaPinThumbnail, FloorPlanAreaPin, FloorPlanArea, Media
from api.services.base_entity_service import BaseEntityService
from api.services.media_entity_service import MediaEntityService

ImageFile.LOAD_TRUNCATED_IMAGES = True


class FloorPlanAreaPinThumbnailEntityService(BaseEntityService):
    model = FloorPlanAreaPinThumbnail
    thumbnail_sizes = (188, 188)
    thumbnail_size_multiplier = 3
    pin_dot_coordinate_diff = 18
    ellipse_filling_color = (0, 162, 224)
    ellipse_border_width = 9

    def recreate_from_area(self, floor_plan_area: FloorPlanArea) -> None:
        pins = FloorPlanAreaPin.objects.filter(floor_plan_area=floor_plan_area).all()
        for pin in pins:
            self.model.objects.filter(floor_plan_area_pin=pin).delete()
            self.create_from_pin(pin)

    def recreate_from_pin(self, pin: FloorPlanAreaPin) -> None:
        self.model.objects.filter(floor_plan_area_pin=pin).delete()
        self.create_from_pin(pin)

    def create_temporary_pin_thumbnail(self, validated_data: dict) -> list[Media]:
        floor_plan_image = validated_data['floor_plan'].get_floor_plan_image()

        if not floor_plan_image:
            raise ValueError('Floor plan image for floor plan %s does not exist.' % validated_data['floor_plan'].pk)

        storage = floor_plan_image.get_common_storage()
        image = Image.open(storage.open(floor_plan_image.link))
        original_image_width, original_image_height = image.size
        name = 'temp-pin-thumb-%s' % floor_plan_image.name
        images = []

        if self.model.Type.GENERAL in validated_data['type']:
            general_thumbnail_image = image
            self._add_thumbnail(general_thumbnail_image)
            self._add_pin_dot(general_thumbnail_image, original_image_width, original_image_height, validated_data['pin_coordinates'])
            general_thumbnail = (self._create_thumbnail_media(general_thumbnail_image, name))
            general_thumbnail.type = self.model.Type.GENERAL.value
            images.append(general_thumbnail)

            general_thumbnail_image.close()
            gc.collect()

        if self.model.Type.AREA in validated_data['type']:
            area_thumbnail_image = Image.open(storage.open(floor_plan_image.link)) if self.model.Type.GENERAL in validated_data['type'] else image
            area_thumbnail_image = self._cut_pin_area(image=area_thumbnail_image, pin_coordinates=validated_data['pin_coordinates'], floor_plan_area=validated_data['floor_plan_area'])
            area_thumbnail = (self._create_thumbnail_media(area_thumbnail_image, name))
            area_thumbnail.type = self.model.Type.AREA.value
            images.append(area_thumbnail)

            area_thumbnail_image.close()
            gc.collect()

        image.close()
        gc.collect()

        return images

    def create_from_pin(self, pin: FloorPlanAreaPin) -> None:
        floor_plan_image = pin.floor_plan_area.floor_plan.get_floor_plan_image()

        if not floor_plan_image:
            raise ValueError('Floor plan image for floor plan %s does not exist.' % pin.floor_plan_area.floor_plan.pk)

        storage = floor_plan_image.get_common_storage()
        image = Image.open(storage.open(floor_plan_image.link))
        original_image_width, original_image_height = image.size

        self._create_area_pin_thumbnail(image.copy(), pin, floor_plan_image.name)
        self._create_general_pin_thumbnail(image.copy(), original_image_width, original_image_height, pin, floor_plan_image)

        image.close()

    def _create_thumbnail_media(self, image: Image, name) -> Media:
        content = io.BytesIO()
        image.save(content, format='PNG', quality='maximum', optimize=True, progressive=True)
        file = SimpleUploadedFile(content=content.getvalue(), name=name, content_type='image/png')
        data = {
            'file': file,
            'is_public': False
        }
        return MediaEntityService().create(data, create_thumbnail=False)

    def _create_general_pin_thumbnail(self, image: Image, width, height, pin, floor_plan_image) -> None:
        self._add_thumbnail(image)
        self._add_pin_dot(image, width, height, pin.pin)
        self._create_pin_thumbnail(image, pin, floor_plan_image.name, FloorPlanAreaPinThumbnail.Type.GENERAL)

        image.close()

    def _create_area_pin_thumbnail(self, image: Image, pin: FloorPlanAreaPin, name) -> None:
        image = self._cut_pin_area(image=image, pin_coordinates=pin.pin, floor_plan_area=pin.floor_plan_area)
        self._create_pin_thumbnail(image, pin, name, FloorPlanAreaPinThumbnail.Type.AREA)

        image.close()

    def _cut_pin_area(self, image: Image, pin_coordinates: dict, floor_plan_area: FloorPlanArea) -> Image:
        area_polygon_points = list(map(operator.itemgetter('x', 'y'), floor_plan_area.polygon['points']))

        cropped_image_box = self._get_cropped_image_box(area_polygon_points)
        image = image.crop(box=(cropped_image_box['left'],
                                cropped_image_box['top'],
                                cropped_image_box['right'],
                                cropped_image_box['bottom']))

        cropped_point_coordinates = {
            'x': pin_coordinates['x'] - cropped_image_box['left'],
            'y': pin_coordinates['y'] - cropped_image_box['top']
        }

        original_width, original_height = image.size

        self._add_thumbnail(image)
        self._add_pin_dot(image, original_width, original_height, cropped_point_coordinates)

        return image

    def _create_pin_thumbnail(self, image: Image, pin, name: str, thumbnail_type: FloorPlanAreaPinThumbnail.Type) -> None:
        thumbnail = self._create_thumbnail_media(image, name)
        self.create({
            'thumbnail': thumbnail,
            'floor_plan_area_pin': pin,
            'type': thumbnail_type
        })

    def _add_thumbnail(self, image: Image) -> None:
        image.thumbnail(
            (self.thumbnail_sizes[0] * self.thumbnail_size_multiplier,
             self.thumbnail_sizes[1] * self.thumbnail_size_multiplier),
            Image.ANTIALIAS
        )

    def _add_pin_dot(self, image: Image, original_width, original_height, point_coordinates) -> None:
        changed_width, changed_height = image.size
        pin_changed_x = changed_width / original_width * point_coordinates['x']
        pin_changed_y = changed_height / original_height * point_coordinates['y']

        ellipse_points = (
            pin_changed_x - self.pin_dot_coordinate_diff,
            pin_changed_y - self.pin_dot_coordinate_diff,
            pin_changed_x + self.pin_dot_coordinate_diff,
            pin_changed_y + self.pin_dot_coordinate_diff
        )

        draw_image = ImageDraw.Draw(image, 'RGBA')
        draw_image.ellipse(ellipse_points, fill=self.ellipse_filling_color, outline='white', width=self.ellipse_border_width)

    def _get_cropped_image_box(self, polygon_points: list) -> dict:
        top = min(map(operator.itemgetter(1), polygon_points))
        left = min(map(operator.itemgetter(0), polygon_points))
        bottom = max(map(operator.itemgetter(1), polygon_points))
        right = max(map(operator.itemgetter(0), polygon_points))

        return {
            'left': left * 0.9,
            'top': top * 0.9,
            'right': right * 1.1,
            'bottom': bottom * 1.1,
        }
