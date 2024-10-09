from django.db import models
from django.db.models import UniqueConstraint
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class AssetRegister(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'asset_registers'
        constraints = [
            UniqueConstraint(fields=['project'],
                             name='asset_register_uniqueness',
                             condition=models.Q(deleted__isnull=True))
        ]

    data = models.JSONField()
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
