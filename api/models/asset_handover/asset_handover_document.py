from django.db import models
from django.db.models import Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class AssetHandoverDocument(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_documents'
        constraints = [
            models.UniqueConstraint(
                fields=('asset_handover', 'document_type',),
                name='asset_handover_document_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    asset_handover = models.ForeignKey('AssetHandover', on_delete=models.CASCADE)
    number_required_files = models.IntegerField(default=0)
    document_type = models.ForeignKey('AssetHandoverDocumentType', on_delete=models.CASCADE)
