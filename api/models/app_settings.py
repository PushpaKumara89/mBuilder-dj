from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class AppSettings(BaseModel):
    _safedelete_policy = SOFT_DELETE
    disable_user_registration_from_mobile_devices = models.BooleanField(_('Disable user registration from mobile devices'), default=False)

    class Meta:
        db_table = 'app_settings'
