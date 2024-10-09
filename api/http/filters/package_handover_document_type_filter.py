from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import User, PackageHandoverDocumentType, PackageHandoverDocumentGroup


class PackageHandoverDocumentTypeFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('id', 'id',),
            ('name', 'name',),
            ('group', 'group',),
            ('created_at', 'created_at',),
        ),
    )

    user_group = rest_framework.MultipleChoiceFilter(method='filter_by_user_group',
                                                     choices=User.Group.choices,
                                                     widget=QueryArrayWidget)
    group = rest_framework.ModelMultipleChoiceFilter(
        queryset=PackageHandoverDocumentGroup.objects.all(),
        field_name='group',
        widget=QueryArrayWidget
    )

    def filter_by_user_group(self, queryset, name, value):
        if value:
            doc_groups = []

            for user_group in value:
                if doc_group := PackageHandoverDocumentGroup.GROUPS_MAP.get(int(user_group)):
                    doc_groups += doc_group

            if doc_groups:
                queryset = queryset.filter(group__in=doc_groups)

        return queryset

    class Meta:
        model = PackageHandoverDocumentType
        fields = ('id', 'name', 'group',)
