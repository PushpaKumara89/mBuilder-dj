from django_filters import rest_framework

from api.models import Recipient


class RecipientFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
        ),
    )

    class Meta:
        model = Recipient
        fields = ('email', 'first_name', 'last_name',)
