from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.validators import qs_filter, qs_exists


class ExistsValidator:
    """
    Validator that corresponds to `exist=True` on a model.

    Should be applied to an individual field on the serializer.
    """
    message = _('Entity does not exist.')
    requires_context = True

    def __init__(self, queryset, message=None, lookup='exact'):
        self.queryset = queryset
        self.message = message or self.message
        self.lookup = lookup

    def filter_queryset(self, value, queryset, field_name):
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {'%s__%s' % (field_name, self.lookup): value}
        return qs_filter(queryset, **filter_kwargs)

    def __call__(self, value, serializer_field):
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        field_name = serializer_field.source_attrs[-1]

        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset, field_name)
        if not qs_exists(queryset):
            raise ValidationError(self.message, code='exists')

    def __repr__(self):
        return '<%s(queryset=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        )
