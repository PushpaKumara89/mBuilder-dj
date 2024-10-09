from django.db import models
from safedelete import SOFT_DELETE
from api.models.base_model import BaseModel
from api.models.managers.recipient import RecipientManager


class Recipient(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'recipients'

    objects = RecipientManager()

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
