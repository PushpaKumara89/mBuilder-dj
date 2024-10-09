from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class PackageHandoverDocument(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_documents'

    package_handover = models.ForeignKey('PackageHandover', on_delete=models.CASCADE)
    package_handover_document_type = models.ForeignKey('PackageHandoverDocumentType', on_delete=models.CASCADE)
    number_required_files = models.PositiveIntegerField(default=0)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)

    @property
    def get_media(self):
        return self.packagehandoverdocumentmedia_set.first()
