from django import forms
from django_filters import filters


class NonValidatingMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class NonValidatingMultipleChoiceFilter(filters.MultipleChoiceFilter):
    field_class = NonValidatingMultipleChoiceField
