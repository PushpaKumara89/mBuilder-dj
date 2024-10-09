from django.contrib.auth.models import AbstractUser, Group as UserGroup
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import UserManager
from api.models.queryset.user_queryset import UserQueryset


class User(AbstractUser, BaseModel):
    send_registration_emails = True

    _safedelete_policy = SOFT_DELETE

    class Group(models.IntegerChoices):
        COMPANY_ADMIN = 1, _('Company Admin')
        ADMIN = 2, _('Admin')
        MANAGER = 3, _('Manager')
        SUBCONTRACTOR = 4, _('Subcontractor')
        CLIENT = 5, _('Client')
        CONSULTANT = 6, _('Consultant')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    class Meta(BaseModel.Meta):
        db_table = 'auth_user'
        ordering = ('id',)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = UserManager(UserQueryset)
    username = None
    email = models.EmailField(unique=True, null=True)
    phone = PhoneNumberField(null=True)
    position = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING.value)
    company = models.ForeignKey('Company', on_delete=models.DO_NOTHING, null=True)
    group = models.ForeignKey(UserGroup, null=True, on_delete=models.SET_NULL, related_name='related_user')

    def get_group_label(self) -> str:
        if self.group_id is None:
            return ''
        return dict(self.Group.choices)[self.group_id]

    @property
    def is_company_admin(self):
        return self.group_id == self.Group.COMPANY_ADMIN.value

    @property
    def is_admin(self):
        return self.group_id == self.Group.ADMIN.value

    @property
    def is_manager(self):
        return self.group_id == self.Group.MANAGER.value

    @property
    def is_subcontractor(self):
        return self.group_id == self.Group.SUBCONTRACTOR.value

    @property
    def is_client(self):
        return self.group_id == self.Group.CLIENT.value

    @property
    def is_consultant(self):
        return self.group_id == self.Group.CONSULTANT.value

    @property
    def is_multiplex(self):
        return self.group_id in [self.Group.COMPANY_ADMIN.value, self.Group.ADMIN.value, self.Group.MANAGER.value]
