from django_filters import rest_framework


class TaskUpdateFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('created_at', 'created_at',),
            ('updated_at', 'updated_at',),
        ),
    )
