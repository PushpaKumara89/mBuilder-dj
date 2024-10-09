from django.contrib.auth.base_user import BaseUserManager
from django.db.models import QuerySet
from safedelete.managers import SafeDeleteManager


class UserManager(BaseUserManager, SafeDeleteManager):
    def create_user(self, email, password=None, is_superuser=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active
        user.save(using=self._db)

        return user

    def create_superuser(self, **kwargs):
        return self.create_user(is_superuser=True, is_staff=True, **kwargs)

    def get_by_natural_key(self, username):
        return self.filter(deleted__isnull=True).get(**{self.model.USERNAME_FIELD + '__iexact': username})

    def only_active(self) -> QuerySet:
        return self.get_queryset().filter(is_active=True)
