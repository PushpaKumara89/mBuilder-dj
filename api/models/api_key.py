from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class ApiKey(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'api_keys'

    token = models.UUIDField(editable=False, unique=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    expires_at = models.DateField()
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    has_access_to_project = models.BooleanField(default=False)
    has_access_to_package_handover = models.BooleanField(default=False)
    has_access_to_asset_handover = models.BooleanField(default=False)
    has_access_to_quality_issue = models.BooleanField(default=False)
