from django.db import models
from django.db.models import UniqueConstraint
from safedelete import HARD_DELETE

from api.models.base_model import BaseModel


class ResponseCategory(BaseModel):
    _safedelete_policy = HARD_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'response_category'
        constraints = [
            UniqueConstraint(fields=['name', 'project'],
                             name='response_category_uniqueness',
                             condition=models.Q(deleted__isnull=True))
        ]

    name = models.CharField(max_length=255)
    description = models.TextField(default=None, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
