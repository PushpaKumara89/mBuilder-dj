from django.db import models
from django.db.models import UniqueConstraint
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class Company(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'companies'
        constraints = [
            UniqueConstraint(fields=['name'],
                             name='companies_uniqueness',
                             condition=models.Q(deleted__isnull=True))
        ]

    name = models.CharField(max_length=255)
