from django.db.models import Subquery, OuterRef
from django_filters import OrderingFilter

from api.models import TaskUpdate


class TaskOrderFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('comment', 'Comment'),
            ('-comment', 'Comment (descending)'),
        ]

    def filter(self, qs, value):
        if value is not None and any(v in ['comment', '-comment'] for v in value):
            qs = qs.annotate(comment=Subquery(
                TaskUpdate.objects.filter(task__pk=OuterRef('pk')).order_by('-created_at').values('comment')[:1]
            ))

        return super().filter(qs, value)
