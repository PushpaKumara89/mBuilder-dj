from django.db.models import Count
from django_filters import OrderingFilter


class PackageActivityOrderingFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('tasks_count', 'Tasks count'),
            ('-tasks_count', 'Tasks count (descending)'),
        ]

    def filter(self, qs, value):
        if value is not None and any(v in ['tasks_count', '-tasks_count'] for v in value):
            qs = qs.annotate(tasks_count=Count('packageactivitytask'))

        return super().filter(qs, value)
