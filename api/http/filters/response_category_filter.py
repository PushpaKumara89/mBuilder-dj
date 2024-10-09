from django_filters import rest_framework

from api.models import ResponseCategory


class ResponseCategoryFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('name', 'name',),
            ('description', 'description',),
            ('created_at', 'created_at',),
        ),
    )

    class Meta:
        model = ResponseCategory
        fields = ('name', 'description',)
