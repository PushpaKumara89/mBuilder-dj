from django_filters.rest_framework import FilterSet, OrderingFilter

from api.models import Media


class MediaFilter(FilterSet):
    sort = OrderingFilter(
        fields=(
            ('name', 'name'),
        ),
    )

    class Meta:
        model = Media
        fields = ('name',)
