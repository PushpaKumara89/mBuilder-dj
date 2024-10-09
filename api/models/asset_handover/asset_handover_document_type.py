from enum import Enum

from django.db import models
from django.db.models import Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class AssetHandoverDocumentType(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_document_types'
        constraints = [
            models.UniqueConstraint(
                fields=('name',),
                name='asset_handover_document_type_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    class Types(Enum):
        ASBUILT_DRAWING = 1
        TEST_PACK = 2

    name = models.CharField(max_length=255)
