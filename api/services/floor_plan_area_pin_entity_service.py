from typing import Optional, Dict, Type

from django.contrib.contenttypes.models import ContentType

from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_change_serializer import \
    FloorPlanAreaPinChangeSerializer
from api.http.serializers.floor_plan_area_pin.floor_plan_area_pin_serializer import FloorPlanAreaPinSerializer
from api.models import FloorPlanAreaPin, Subtask, QualityIssue
from api.models.base_model import BaseModel
from api.services.base_entity_service import BaseEntityService
from api.services.floor_plan_area_pin_thumbnail_entity_service import FloorPlanAreaPinThumbnailEntityService


class FloorPlanAreaPinEntityService(BaseEntityService):
    model = FloorPlanAreaPin

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        pin = super().create(validated_data, **kwargs)
        FloorPlanAreaPinThumbnailEntityService().create_from_pin(pin)
        return pin

    def create_or_update(self, existing_entity: Optional, validated_data: dict, **kwargs):
        if existing_entity:
            return self.update(existing_entity, validated_data, **kwargs)
        else:
            return self.create(validated_data, **kwargs)

    def update(self, instance: Type[BaseModel], validated_data: Dict, **kwargs) -> Type[BaseModel]:
        updated_pin = super().update(instance, validated_data, **kwargs)
        FloorPlanAreaPinThumbnailEntityService().recreate_from_pin(updated_pin)
        return updated_pin

    def create_for_subtask(self, validate_data: dict, **kwargs):
        subtask_content_type = ContentType.objects.get_for_model(Subtask)
        validate_data['content_type'] = subtask_content_type
        validate_data['object_id'] = validate_data['object_id'].pk

        return self.create(validate_data, **kwargs)

    def create_for_quality_issue(self, validate_data: dict, **kwargs):
        subtask_content_type = ContentType.objects.get_for_model(QualityIssue)
        validate_data['content_type'] = subtask_content_type
        validate_data['object_id'] = validate_data['object_id'].pk

        return self.create(validate_data, **kwargs)

    def create_or_update_from_quality_issue_update(self, quality_issue_update_validated_data: dict, user):
        floor_plan_area_pin_data = quality_issue_update_validated_data['new_data']['floor_plan_area_pin']
        floor_plan_area_pin_data['object_id'] = quality_issue_update_validated_data['quality_issue'].pk
        if 'floor_plan_area' in floor_plan_area_pin_data:
            floor_plan_area_pin_data['floor_plan_area'] = (
                floor_plan_area_pin_data['floor_plan_area']
                if type(floor_plan_area_pin_data['floor_plan_area']) is int
                else floor_plan_area_pin_data['floor_plan_area'].pk
            )

        if quality_issue_update_validated_data['quality_issue'].floor_plan_area_pin:
            floor_plan_area_pin_serializer = FloorPlanAreaPinChangeSerializer(data=floor_plan_area_pin_data)
            floor_plan_area_pin_serializer.is_valid(raise_exception=True)
        else:
            content_type = ContentType.objects.get_for_model(QualityIssue)
            floor_plan_area_pin_data['content_type'] = content_type.pk
            floor_plan_area_pin_serializer = FloorPlanAreaPinSerializer(data=floor_plan_area_pin_data)
            floor_plan_area_pin_serializer.is_valid(raise_exception=True)

        return self.create_or_update(
            quality_issue_update_validated_data['quality_issue'].floor_plan_area_pin,
            floor_plan_area_pin_serializer.validated_data,
            user=user
        )

    def create_or_update_from_subtask_update(self, subtask_update_validated_data: dict, user):
        floor_plan_area_pin_data = subtask_update_validated_data['new_data']['floor_plan_area_pin']
        floor_plan_area_pin_data['object_id'] = subtask_update_validated_data['subtask'].pk
        if 'floor_plan_area' in floor_plan_area_pin_data:
            floor_plan_area_pin_data['floor_plan_area'] = (
                floor_plan_area_pin_data['floor_plan_area']
                if type(floor_plan_area_pin_data['floor_plan_area']) is int
                else floor_plan_area_pin_data['floor_plan_area'].pk
            )

        if subtask_update_validated_data['subtask'].floor_plan_area_pin:
            floor_plan_area_pin_serializer = FloorPlanAreaPinChangeSerializer(data=floor_plan_area_pin_data)
            floor_plan_area_pin_serializer.is_valid()
        else:
            content_type = ContentType.objects.get_for_model(Subtask)
            floor_plan_area_pin_data['content_type'] = content_type.pk
            floor_plan_area_pin_serializer = FloorPlanAreaPinSerializer(data=floor_plan_area_pin_data)
            floor_plan_area_pin_serializer.is_valid()

        return self.create_or_update(
            subtask_update_validated_data['subtask'].floor_plan_area_pin,
            floor_plan_area_pin_serializer.validated_data,
            user=user
        )
