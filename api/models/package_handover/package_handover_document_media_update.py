from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class PackageHandoverDocumentMediaUpdate(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_document_media_updates'

    package_handover_document_media = models.ForeignKey('PackageHandoverDocumentMedia', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    old_data = models.JSONField()
    new_data = models.JSONField()
