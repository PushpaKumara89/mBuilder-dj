from typing import Dict, Type

import reversion

from api.models import FloorPlanArea, User, FloorPlanRevisionMeta
from api.models.base_model import BaseModel
from api.services.base_entity_service import BaseEntityService


class FloorPlanAreaEntityService(BaseEntityService):
    model: FloorPlanArea = FloorPlanArea

    def perform_actions(self, validated_data: dict, user: User):
        creation_data = validated_data.get('create', [])
        update_data = validated_data.get('update', [])
        deletion_data = validated_data.get('delete', [])

        with reversion.create_revision():
            reversion.set_user(user)
            if creation_data:
                self.create_many(creation_data, user=user)

            for data in update_data:
                instance = data.pop('id')
                self.update(instance, data, user=user)

            if deletion_data:
                self.model.objects.filter(id__in=[obj['id'].id for obj in deletion_data]).delete()

            if any((creation_data, update_data, deletion_data)):
                reversion.add_meta(FloorPlanRevisionMeta, event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value)

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        with reversion.create_revision():
            entity = super().create(validated_data, **kwargs)
            reversion.set_user(kwargs.get('user'))

        return entity

    def destroy(self, instance, **kwargs) -> None:
        with reversion.create_revision():
            instance.delete()
            reversion.add_meta(FloorPlanRevisionMeta, event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value)
            reversion.set_user(kwargs.get('user'))

    # def update(self, instance: Type[BaseModel], validated_data: Dict, **kwargs) -> Type[BaseModel]:
    #     points_before_update = instance.polygon['points']
    #     updated_area = super().update(instance, validated_data, **kwargs)
    #     points_after_update = updated_area.polygon['points']
    #
    #     if points_after_update != points_before_update:
    #         if FloorPlanAreaPin.objects.filter(floor_plan_area=instance).exists():
    #             FloorPlanAreaPinThumbnailEntityService().regenerate_from_area(instance)
    #
    #     return updated_area
