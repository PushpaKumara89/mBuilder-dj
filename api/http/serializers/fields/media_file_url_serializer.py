from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from rest_framework import fields
from django.core.validators import URLValidator


class MediaFileUrl(fields.CharField):
    def to_representation(self, value):
        validate = URLValidator()
        try:
            validate(value)
            return value
        except ValidationError:
            return str(default_storage.url(value))
