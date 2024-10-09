from django.db import models
from safedelete import SOFT_DELETE
from django.utils.translation import gettext_lazy as _

from api.models.base_model import BaseModel


class PackageHandover(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class InspectionPeriod(models.IntegerChoices):
        ZERO = 0, _('Not Required')
        ONE = 1, _('One')
        THREE = 3, _('Three')
        SIX = 6, _('Six')
        TWELVE = 12, _('Twelve')
        EIGHTEEN = 18, _('Eighteen')

        __empty__ = _('Undefined')

    class MaintenancePeriod(models.IntegerChoices):
        ZERO = 0, _('Not Required')
        ONE = 1, _('One')
        THREE = 3, _('Three')
        SIX = 6, _('Six')
        TWELVE = 12, _('Twelve')
        EIGHTEEN = 18, _('Eighteen')

        __empty__ = _('Undefined')

    class Meta(BaseModel.Meta):
        db_table = 'package_handovers'

    inspection_period = models.IntegerField(choices=InspectionPeriod.choices, null=True, default=None)
    maintenance_period = models.IntegerField(choices=MaintenancePeriod.choices, null=True, default=None)
    package_matrix = models.ForeignKey('PackageMatrix', on_delete=models.CASCADE)
