from enum import Enum

from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.user import User


class PackageHandoverDocumentGroup(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Group(Enum):
        SUBCONTRACTOR_DOCUMENT = 1
        CONSULTANT_DOCUMENT = 2
        H_AND_S_CONSULTANT_DOCUMENT = 3
        MULTIPLEX_DOCUMENTS = 4

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_document_groups'

    GROUPS_MAP = {
        User.Group.SUBCONTRACTOR.value: [Group.SUBCONTRACTOR_DOCUMENT.value],
        User.Group.CONSULTANT.value: [Group.CONSULTANT_DOCUMENT.value,
                                      Group.H_AND_S_CONSULTANT_DOCUMENT.value]
    }

    name = models.CharField(max_length=255)
