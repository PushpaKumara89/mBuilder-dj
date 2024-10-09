from django.db.models.expressions import Exists, OuterRef
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.number_in_filter import NumberInFilter
from api.models import Company, Project, User, PackageActivity, PackageMatrixCompany


class CompanyFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name',),
            ('created_at', 'created_at',),
        ),
    )

    id = NumberInFilter(
        field_name='id',
        widget=QueryArrayWidget
    )

    name = rest_framework.CharFilter(field_name='name', lookup_expr='iexact')
    subcontractors_in_project = rest_framework.NumberFilter(method='filter_by_subcontractors_in_project')
    clients_in_project = rest_framework.NumberFilter(method='filter_by_clients_in_project')
    companies_of_package_activities = rest_framework.ModelChoiceFilter(queryset=PackageActivity.objects.all(),
                                                                       method='filter_by_package_activity')

    def filter_by_package_activity(self, queryset, name, value):
        if value:
            filters = {
                'company': OuterRef('id'),
                'package_matrix__package_activity': value
            }

            default_filters = {
                'company': OuterRef('pk'),
                'group': User.Group.SUBCONTRACTOR.value
            }

            if 'project' in self.request.query_params:
                filters['package_matrix__project'] = self.request.query_params['project']
                default_filters['project'] = self.request.query_params['project']

            package_matrix_company_companies_query = queryset.annotate(assigned_to_activity=Exists(
                PackageMatrixCompany.objects.filter(**filters))).filter(assigned_to_activity=True)

            if package_matrix_company_companies_query.count() > 0:
                return package_matrix_company_companies_query

            return queryset.filter(Exists(User.objects.filter(**default_filters)))

        return queryset

    def filter_by_subcontractors_in_project(self, queryset, name, value):
        if value and int(value) > 0:
            return queryset.filter(Exists(Project.objects.filter(pk=int(value),
                                                                 users__company=OuterRef('pk'),
                                                                 users__group=User.Group.SUBCONTRACTOR.value)))

        return queryset

    def filter_by_clients_in_project(self, queryset, name, value):
        if value and int(value) > 0:
            return queryset.filter(Exists(Project.objects.filter(pk=int(value),
                                                                 users__company=OuterRef('pk'),
                                                                 users__group=User.Group.CLIENT.value)))

        return queryset

    class Meta:
        model = Company
        fields = ('name',)
