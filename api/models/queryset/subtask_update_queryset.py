from django.db.models import Q
from django.db.models.expressions import RawSQL

from api.models.queryset import SafeDeleteQueryset


class SubtaskUpdateQueryset(SafeDeleteQueryset):
    def get_with_changed_status_in_desc_order(self):
        return self.filter(~Q(
            old_data__status=RawSQL('new_data -> %s', ('status',))
        )).order_by('-created_at')
