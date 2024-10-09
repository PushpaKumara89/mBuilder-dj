from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr


class DateAfterValidator:
    """
    Validator for checking if an end date is after a start date field.
    Implementation based on `UniqueTogetherValidator` of Django Rest Framework.
    """
    message = _('{date_after} should be after {start_date}.')

    def __init__(self, start_date, date_after, message=None):
        self.start_date = start_date
        self.date_after = date_after
        self.message = message or self.message

    def __call__(self, attrs, serializer):
        instance = serializer.instance

        if self.date_after in attrs and self.start_date in attrs:
            if attrs[self.date_after] <= attrs[self.start_date]:
                self.__raise_error()
        elif instance is not None:
            self.__check_valid_instance_data(attrs, instance)

    def __check_valid_instance_data(self, data, instance):
        if self.__is_start_date_greater(data, instance) or self.__is_date_after_less(data, instance):
            self.__raise_error()

    def __is_start_date_greater(self, data, instance):
        return self.start_date in data and data[self.start_date] >= getattr(instance, self.date_after)

    def __is_date_after_less(self, data, instance):
        return self.date_after in data and data[self.date_after] <= getattr(instance, self.start_date)

    def __raise_error(self):
        message = self.message.format(
            date_after=self.date_after,
            start_date=self.start_date,
        )

        raise ValidationError(
            {self.date_after: message},
            code='date_after',
        )

    def __repr__(self):
        return '<%s(start_date=%s, date_after=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.date_after),
            smart_repr(self.start_date)
        )
