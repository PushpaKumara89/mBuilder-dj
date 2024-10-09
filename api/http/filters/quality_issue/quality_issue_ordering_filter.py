from django_filters import OrderingFilter


class QualityIssueOrderingFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('default_sort', 'Default sort',),
        ]

    def filter(self, qs, value):
        if value is not None:
            if 'default_sort' in value:
                # Exclude this field from the list to avoid error for non-existing sortable field.
                # Sort by this parameter moved to SubtaskViewSet.
                value = [sort_field for sort_field in value if sort_field != 'default_sort']

        return super().filter(qs, value)
