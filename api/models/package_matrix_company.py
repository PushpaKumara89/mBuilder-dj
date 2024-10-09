from django.db import models
from django.db.models import Q
from safedelete import HARD_DELETE

from api.models.base_model import BaseModel


class PackageMatrixCompany(BaseModel):
    _safedelete_policy = HARD_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_matrix_company'
        constraints = [
            models.UniqueConstraint(
                fields=('package_matrix', 'company',),
                name='package_matrix_company_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    package_matrix = models.ForeignKey('PackageMatrix', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
