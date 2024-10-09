from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class PackageHandoverDocumentType(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_document_types'

    name = models.CharField(max_length=255)
    group = models.ForeignKey('PackageHandoverDocumentGroup', on_delete=models.CASCADE)
