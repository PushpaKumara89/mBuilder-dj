from django.db import models
from safedelete import HARD_DELETE

from api.models.base_model import BaseModel


class PackageMatrixHiddenActivityTask(BaseModel):
    _safedelete_policy = HARD_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_matrix_hidden_activity_tasks'
        constraints = [
            models.UniqueConstraint(
                fields=['package_matrix', 'package_activity_task'],
                name='package_matrix_hidden_activity_tasks_unique'
            )
        ]

    package_matrix = models.ForeignKey('PackageMatrix', on_delete=models.CASCADE)
    package_activity_task = models.ForeignKey('PackageActivityTask', on_delete=models.CASCADE)
