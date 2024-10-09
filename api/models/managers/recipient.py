from django.db.models import QuerySet, Q
from api.models.managers import BaseManager


class RecipientManager(BaseManager):
    def only_active(self) -> QuerySet:
        return self.get_queryset().filter((Q(user__is_active=True) | Q(user__isnull=True)))
