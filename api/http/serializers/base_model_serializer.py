import pydash
from rest_flex_fields import FlexFieldsModelSerializer, EXPAND_PARAM
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField, DateTimeField
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta


class BaseModelSerializer(FlexFieldsModelSerializer):
    id = ReadOnlyField()
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        if EXPAND_PARAM in kwargs:
            kwargs[EXPAND_PARAM] = self.filter_expandable_fields(kwargs.get(EXPAND_PARAM, []))

        super().__init__(*args, **kwargs)

    def filter_expandable_fields(self, expandable_params: list):
        def expandable_field_exists(expand_field):
            return hasattr(self.Meta, 'expandable_fields') \
               and expand_field.split('.')[0] in self.Meta.expandable_fields.keys()

        return list(
            filter(expandable_field_exists, expandable_params)
        )

    def non_field_fail(self, name: str, error_key: str = None):
        error_key = name if error_key is None else error_key
        message = self.default_error_messages[error_key]

        raise ValidationError({name: message})

    # Rewrite basic update to pass update fields to the model's `save` method.
    # These fields needed us to determine event's type.
    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        update_fields = []
        update_fields_original_values = {}
        fields = list(info.fields.keys())

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                # Exclude immutable model fields.
                if attr in fields or attr in info.relations:
                    update_fields.append(attr)
                    update_fields_original_values[attr] = getattr(instance, attr)

                setattr(instance, attr, value)

        if pydash.get(instance, 'updated_at') and 'updated_at' not in update_fields:
            update_fields.append('updated_at')

        instance.update_fields_original_values = update_fields_original_values
        instance.save(update_fields=update_fields)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
