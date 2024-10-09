from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class HandoverDocument(BaseModel):
    class Entities(TextChoices):
        ASSET_HANDOVER = 'asset_handover', _('Asset handover')
        PACKAGE_HANDOVER = 'package_handover', _('Package handover')

    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'handover_documents'

    entity = models.CharField(choices=Entities.choices, max_length=255, null=True)
    entity_id = models.PositiveIntegerField()
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    building = models.CharField(max_length=255, null=True)
    level = models.CharField(max_length=255, null=True)
    area = models.CharField(max_length=255, null=True)

    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    media = models.ForeignKey('Media', on_delete=models.CASCADE)
    document_type = models.PositiveIntegerField()

    filename = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, null=True)
    information = models.TextField(null=True, blank=True)

    @property
    def file_type(self):
        return self.filename.split('.')[-1]

    @property
    def is_asset_handover_entity(self) -> bool:
        return self.entity == self.Entities.ASSET_HANDOVER

    @property
    def is_package_handover_entity(self) -> bool:
        return self.entity == self.Entities.PACKAGE_HANDOVER
