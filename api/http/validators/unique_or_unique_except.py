from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.validators import qs_filter, qs_exists


class UniqueOrUniqueExceptValidator:
    """
    Validator that corresponds to `unique=True` on a model field.

    Should be applied to an individual field on the serializer.
    """
    message = _('This field must be unique.')
    requires_context = True

    def __init__(self, queryset, unique_ignore='id', message=None, lookup='exact'):
        self.queryset = queryset
        self.message = message or self.message
        self.lookup = lookup
        self.unique_ignore = unique_ignore

    def filter_queryset(self, value, queryset, field_name):
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {'%s__%s' % (field_name, self.lookup): value}
        return qs_filter(queryset, **filter_kwargs)

    def exclude_current_instance(self, queryset, instance):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        if instance is not None:
            return queryset.exclude(pk=instance.pk)
        return queryset

    def exclude_current(self, queryset, serializer_field, field_name, value):
        initial_data = serializer_field.parent.initial_data

        """
        We use this validation only for SYNC method.
        In this method we expect that data will be the list with objects.
        We skip this validation if initial data is dictionary
        because this type of variable responsible for single creation and update
        """
        if type(initial_data) is dict:
            return queryset

        existing_entity = self.find_item_for_current_validating_field(initial_data, field_name, value)
        if len(existing_entity) > 1:
            raise ValidationError(self.message, code='unique')

        if len(existing_entity) == 1 and self.unique_ignore in existing_entity[0]:
            existing_entity = existing_entity[0]
            queryset = queryset.exclude(**{self.unique_ignore: existing_entity[self.unique_ignore]})

        return queryset

    def find_item_for_current_validating_field(self, initial_data, field_name, value):
        return [
            item for item in initial_data
            if field_name in item and item[field_name] == value
        ]

    def __call__(self, value, serializer_field):
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        field_name = serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer_field.parent, 'instance', None)

        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset, field_name)
        if instance is None:
            queryset = self.exclude_current(queryset, serializer_field, field_name, value)
        else:
            queryset = self.exclude_current_instance(queryset, instance)

        if qs_exists(queryset):
            raise ValidationError(self.message, code='unique')

    def __repr__(self):
        return '<%s(queryset=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        )
