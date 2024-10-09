from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import Project


class ProjectFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
        ),
    )

    status = rest_framework.MultipleChoiceFilter(
        field_name='status', choices=Project.Status.choices, widget=QueryArrayWidget
    )

    class Meta:
        model = Project
        fields = ('name',)
