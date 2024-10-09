from django.db.models import Count, BooleanField, Q, DateTimeField
from django.db.models.expressions import RawSQL, Subquery, OuterRef
from django_filters import OrderingFilter

from api.models import Subtask, SubtaskUpdate


class SubtaskOrderingFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('updated_at', 'Updated at'),
            ('-updated_at', 'Updated at (descending)'),
            ('default_sort', 'Default sort',),
            ('-status_date', 'Status date (descending)'),
            ('status_date', 'Status date',),
        ]

    def filter(self, qs, value):
        if value is not None:
            if any(v in ['updated_at', '-updated_at'] for v in value):
                qs = qs.annotate(closed=RawSQL('"subtasks"."status" = %s', (Subtask.Status.CLOSED,), output_field=BooleanField()))
                value.append('-closed')

            if 'default_sort' in value:
                # Exclude this field from the list to avoid error for non-existing sortable field.
                # Sort by this parameter moved to SubtaskViewSet.
                value = [sort_field for sort_field in value if sort_field != 'default_sort']

            if any(v in ['status_date', '-status_date'] for v in value):
                qs = qs.annotate(status_date=Subquery(SubtaskUpdate.objects.filter(
                    ~Q(old_data__status=RawSQL('new_data -> %s', ('status',))),
                    subtask=OuterRef('id')).order_by('-created_at').values('created_at')[:1],
                    output_field=DateTimeField(null=True, blank=True)
                ))

        return super().filter(qs, value)
