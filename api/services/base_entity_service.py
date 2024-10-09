import traceback

from rest_framework.utils import model_meta
from typing import Dict, List, Type

from api.models.base_model import BaseModel
from api.services.base_entity_sync_service import BaseEntitySyncService


class BaseEntityService:
    model: Type[BaseModel]
    sync_service: Type[BaseEntitySyncService] = BaseEntitySyncService

    def _get_sync_service(self, **kwargs) -> BaseEntitySyncService:
        return self.sync_service(**kwargs)

    def create_many(self, validated_data: List[Dict], **kwargs) -> list:
        return [self.create(entity, **kwargs) for entity in validated_data]

    @staticmethod
    def _set_many_to_many(instance: Type[BaseModel], many_to_many: Dict) -> None:
        for field_name, value in many_to_many.items():
            field = getattr(instance, field_name, None)
            if field is not None:
                field.set(value)

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance
        """
        ModelClass = self.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            when_calling_tpl = f'`{ModelClass.__name__}.{ModelClass._default_manager.name}.create()`'
            msg = (
                f'Got a `TypeError` when calling {when_calling_tpl}. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                f'{when_calling_tpl}. You may need to make the field '
                f'read-only, or override the {self.__class__.__name__}.create() method to handle '
                f'this correctly.\nOriginal exception was:\n {traceback.format_exc()}'
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            self._set_many_to_many(instance, many_to_many)

        return instance

    def update(self, instance: Type[BaseModel], validated_data: Dict, **kwargs) -> Type[BaseModel]:
        info = model_meta.get_field_info(instance)
        update_fields = []
        update_fields_original_values = {}
        fields = list(info.fields.keys())

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        many_to_many = {}
        for field_name, value in validated_data.items():
            if field_name in info.relations and info.relations[field_name].to_many:
                many_to_many[field_name] = value
            else:
                # Exclude immutable model fields.
                if field_name in fields or field_name in info.relations:
                    update_fields.append(field_name)
                    update_fields_original_values[field_name] = getattr(instance, field_name)

                setattr(instance, field_name, value)

        if getattr(instance, 'updated_at', None) and 'updated_at' not in update_fields:
            update_fields.append('updated_at')

        instance.update_fields_original_values = update_fields_original_values
        instance.save(update_fields=update_fields)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance, and we do not want it to collide with .update()
        if many_to_many:
            self._set_many_to_many(instance, many_to_many)

        return instance
