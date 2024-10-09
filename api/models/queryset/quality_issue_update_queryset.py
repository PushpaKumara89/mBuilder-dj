from django.db.models import Q, CharField
from django.db.models.expressions import RawSQL, Value
from django.db.models.functions import Concat

from api.models import QualityIssue
from api.models.queryset import SafeDeleteQueryset


class QualityIssueUpdateQueryset(SafeDeleteQueryset):
    def get_with_changed_status_in_desc_order(self):
        return self.filter(~Q(
            old_data__status=RawSQL('new_data -> %s', ('status',))
        )).order_by('-created_at')

    def get_for_last_recipients(self):
        return self.annotate(transition=Concat(RawSQL('old_data ->> %s', ('status',)),
                                               Value('-'),
                                               RawSQL('new_data ->> %s', ('status',)),
                                               output_field=CharField())). \
            filter(Q(transition=f'{QualityIssue.Status.UNDER_REVIEW}-{QualityIssue.Status.UNDER_REVIEW}') |
                   Q(transition=f'{QualityIssue.Status.CONTESTED}-{QualityIssue.Status.UNDER_REVIEW}') |
                   Q(transition=f'-{QualityIssue.Status.UNDER_REVIEW}')). \
            order_by('-created_at')
