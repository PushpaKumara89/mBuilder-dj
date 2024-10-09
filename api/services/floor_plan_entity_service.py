from typing import Dict, Type

import reversion

from api.models import FloorPlan, FloorPlanRevisionMeta, FloorPlanArea, FloorPlanAreaPin, FloorPlanAreaPinThumbnail
from api.models.base_model import BaseModel
from api.services.base_entity_service import BaseEntityService
from api.services.floor_plan_image_entity_service import FloorPlanImageEntityService


class FloorPlanEntityService(BaseEntityService):
    model: FloorPlan = FloorPlan

    def create_or_update(self, validated_data: dict, user) -> FloorPlan:
        instance = self.model.all_objects.filter(
            project=validated_data['project'],
            package=validated_data['package'],
            building=validated_data['building'],
            level=validated_data['level'],
        ).first()
        if instance:
            if instance.deleted:
                instance.undelete()
            instance = self.update(instance, validated_data, user=user)
        else:
            del validated_data['keep_floor_plan_areas_and_floor_plan_pins']

            instance = self.create(validated_data, user=user)
            if instance.media.is_pdf:
                FloorPlanImageEntityService().create({'media': instance.media})
        return instance

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        with reversion.create_revision():
            entity = super().create(validated_data, **kwargs)
            reversion.set_user(kwargs.get('user'))
            reversion.add_meta(FloorPlanRevisionMeta, event_type=FloorPlanRevisionMeta.EventTypes.FILE_UPLOADED.value)

        return entity

    def update(self, instance: FloorPlan, validated_data: Dict, **kwargs) -> FloorPlan:
        old_media = instance.media
        remove_floor_plan_areas_and_floor_plan_pins = not validated_data.pop('keep_floor_plan_areas_and_floor_plan_pins')

        with reversion.create_revision():
            instance = super().update(instance=instance, validated_data=validated_data)
            if old_media.id != validated_data['media'].id:
                reversion.add_meta(FloorPlanRevisionMeta, event_type=FloorPlanRevisionMeta.EventTypes.FILE_UPDATED.value)

                if instance.media.is_pdf:
                    FloorPlanImageEntityService().create({'media': instance.media})

                if remove_floor_plan_areas_and_floor_plan_pins:
                    FloorPlanAreaPinThumbnail.objects.filter(floor_plan_area_pin__floor_plan_area__floor_plan=instance).delete()
                    FloorPlanAreaPin.objects.filter(floor_plan_area__floor_plan=instance).delete()
                    FloorPlanArea.objects.filter(floor_plan=instance).delete()

            reversion.set_user(kwargs.get('user'))

        return instance
