from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class AssetHandoverDocumentMediaUpdate(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_document_media_updates'

    asset_handover_document_media = models.ForeignKey('AssetHandoverDocumentMedia', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    old_data = models.JSONField()
    new_data = models.JSONField()
