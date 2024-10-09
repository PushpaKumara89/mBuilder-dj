from rest_framework.exceptions import ValidationError
from rest_framework.relations import RelatedField
from rest_framework.validators import UniqueTogetherValidator as BaseValidator, qs_exists, qs_filter


class UniqueTogetherValidator(BaseValidator):
    def __init__(self, queryset, fields, lookup=None, message=None):
        self.queryset = queryset
        self.fields = fields
        self.message = message or self.message
        self.lookup = lookup or 'exact'

    def filter_queryset(self, attrs, queryset, serializer):
        """
        Filter the queryset to all instances matching the given attributes.
        """
        # field names => field sources
        sources = [
            serializer.fields[field_name].source
            for field_name in self.fields
        ]

        # If this is an update, then any unprovided field should
        # have it's value set based on the existing instance attribute.
        if serializer.instance is not None:
            for source in sources:
                if source not in attrs:
                    attrs[source] = getattr(serializer.instance, source)

        # Determine the filter keyword arguments and filter the queryset.
        filter_kwargs = {
            self.__get_source_key(source, serializer): attrs[source]
            for source in sources
        }
        return qs_filter(queryset, **filter_kwargs)

    def find_item_for_current_validating_field(self, initial_data, field_name, value):
        return [
            item for item in initial_data
            if field_name in item and item[field_name] == value
        ]

    def __get_source_key(self, source, serializer):
        if not isinstance(serializer.fields[source], RelatedField):
            return '%s__%s' % (source, self.lookup)

        return source

    def __exclude_existing_record_for_list_update(self, queryset, attrs):
        if 'id' in attrs.keys():
            return queryset.exclude(id=attrs['id'])
        return queryset

    def __exclude_for_castling(self, serializer, attrs, queryset):
        if 'id' in attrs.keys():
            search_condition = {attr_name: attr_value for attr_name, attr_value in attrs.items() if attr_name in self.fields}
            existing_castling_entity = serializer.Meta.model.objects.exclude(pk=attrs['id']).filter(**search_condition).first()

            if existing_castling_entity:
                is_castling_entity_in_request = False
                for entity in serializer.initial_data:
                    if 'id' not in entity:
                        continue

                    if is_castling_entity_in_request := entity['id'] == existing_castling_entity.id:
                        break

                if is_castling_entity_in_request:
                    queryset = queryset.exclude(pk=existing_castling_entity.id)

        return queryset

    def __call__(self, attrs, serializer):
        self.enforce_required_fields(attrs, serializer)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset, serializer)

        # Exclude instance for single update.
        queryset = self.exclude_current_instance(attrs, queryset, serializer.instance)

        queryset = self.__exclude_existing_record_for_list_update(queryset, attrs)

        queryset = self.__exclude_for_castling(serializer, attrs, queryset)
        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and qs_exists(queryset):
            field_names = ', '.join(self.fields)
            message = self.message.format(field_names=field_names)
            raise ValidationError(message, code='unique')
