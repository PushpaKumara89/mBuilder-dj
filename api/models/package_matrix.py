from django.db import models
from django.db.models import Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class PackageMatrix(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_matrix'
        constraints = [
            models.UniqueConstraint(
                fields=('project', 'package', 'package_activity',),
                name='package_matrix_unique',
                condition=Q(deleted__isnull=True)
            ),
            models.UniqueConstraint(
                fields=('project', 'package_activity',),
                name='package_matrix_unique_activity',
                condition=Q(deleted__isnull=True)
            )
        ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)
    companies = models.ManyToManyField('Company', through='PackageMatrixCompany',
                                       through_fields=('package_matrix', 'company',))
