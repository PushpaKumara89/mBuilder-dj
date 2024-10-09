from django.db import models
from django.db.models import Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers.asset_handover_information_manager import AssetHandoverInformationManager


class AssetHandoverInformation(BaseModel):
    _safedelete_policy = SOFT_DELETE

    FILLED_INFO_REQUIRED_FIELDS = ('guid_external_ref', 'warranty', 'manufacture_serial_number', 'model_number')

    objects = AssetHandoverInformationManager()

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_information'
        constraints = [
            models.UniqueConstraint(
                fields=('asset_handover',),
                name='asset_handover_information_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    guid_external_ref = models.TextField(null=True, default=None, blank=True)
    warranty = models.TextField(null=True, default=None, blank=True)
    manufacture_serial_number = models.TextField(null=True, default=None, blank=True)
    model_number = models.TextField(null=True, default=None, blank=True)
    asset_handover = models.OneToOneField('AssetHandover', on_delete=models.CASCADE)

    def are_all_required_fields_filled(self):
        return all(getattr(self, field) is not None for field in self.FILLED_INFO_REQUIRED_FIELDS)

    def are_all_original_values_filled(self):
        return all(value is not None for field, value in self.update_fields_original_values.items())

    def is_any_of_required_fields_empty(self):
        return any(getattr(self, field) is None for field in self.FILLED_INFO_REQUIRED_FIELDS)

    def is_any_of_original_values_empty(self):
        return any(value is None for field, value in self.update_fields_original_values.items())
