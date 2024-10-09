import re
from typing import Any

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.db import models
from django.db.models import UniqueConstraint
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.utilities.storage_utilities import get_common_storage as _get_common_storage


class Media(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'media'
        constraints = [
            UniqueConstraint(fields=['hash'], name='api_media_hash_unique', condition=models.Q(deleted__isnull=True))
        ]

    link = models.CharField(max_length=255)
    original_link = models.CharField(max_length=255, null=True, default=None)
    name = models.CharField(max_length=255)
    size = models.PositiveBigIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    hash = models.CharField(null=True, default=None, max_length=255)
    local_id = models.CharField(null=True, max_length=255)

    @property
    def extension(self) -> str:
        result = re.search(r'.+\.([a-zA-Z0-9]+)', self.name)
        try:
            return result.group(1).lower()
        except AttributeError:
            return ''

    @property
    def is_pdf(self) -> bool:
        return self.extension == 'pdf'

    def get_full_link(self) -> str:
        try:
            URLValidator()(self.link)
            return self.link
        except ValidationError:
            return str(default_storage.url(self.link))

    def get_common_storage(self) -> Any:
        return _get_common_storage(self.is_public)
