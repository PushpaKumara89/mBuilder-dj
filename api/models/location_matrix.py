from django.db import models
from safedelete import SOFT_DELETE_CASCADE

from api.models.base_model import BaseModel


class LocationMatrix(BaseModel):
    """
    Model has generated fields `level_number` and `level_postfix`.
    They are created view raw query in migrations because ORM
    doesn't support this kind of fields.
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = 'location_matrix'
        constraints = [
            models.Index(
                fields=('building', 'level', 'area', 'project',),
                name='location_matrix_unique',
                condition=models.Q(deleted__isnull=True)
            ),
            models.Index(
                fields=('building', 'id'),
                name='location_matrix_building_id_index',
                condition=models.Q(deleted__isnull=True)
            )
        ]

    building = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
