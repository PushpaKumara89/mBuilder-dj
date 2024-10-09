from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import ApiKey, Project, Company


class ApiKeyFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(fields={
        'id': 'id',
        'project': 'project',
        'company': 'project',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'expires_at': 'expires_at',
    })

    project = rest_framework.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        widget=QueryArrayWidget
    )

    company = rest_framework.ModelMultipleChoiceFilter(
        queryset=Company.objects.all(),
        widget=QueryArrayWidget
    )

    expires_at = rest_framework.DateFilter()
    expires_at__lt = rest_framework.DateFilter(lookup_expr='lt', field_name='expires_at')
    expires_at__gt = rest_framework.DateFilter(lookup_expr='gt', field_name='expires_at')

    class Meta:
        model = ApiKey
        fields = ('id', 'project', 'expires_at', 'company')
