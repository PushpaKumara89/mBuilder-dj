from django_filters import NumberFilter, BaseInFilter


class NumberInFilter(NumberFilter, BaseInFilter):
    pass
