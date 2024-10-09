from django.db.models import Q, OuterRef, Exists
from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.models import User, Project, PackageActivity, PackageMatrixCompany, ProjectUser, Company


class UserFilter(rest_framework.FilterSet):
    groups_choices = (
        (1, User.Group.COMPANY_ADMIN.name,),
        (2, User.Group.ADMIN.name,),
        (3, User.Group.MANAGER.name,),
        (4, User.Group.SUBCONTRACTOR.name,),
        (5, User.Group.CLIENT.name,),
        (6, User.Group.CONSULTANT.name,),
    )
    group = rest_framework.MultipleChoiceFilter(field_name='group_id', choices=groups_choices, widget=QueryArrayWidget())
    exclude_group = rest_framework.MultipleChoiceFilter(field_name='group_id', choices=groups_choices,
                                                        widget=QueryArrayWidget(), exclude=True)

    project_or_company_admins = rest_framework.ModelMultipleChoiceFilter(
        field_name='project',
        queryset=Project.objects.all(),
        method="get_by_project_or_company_admins"
    )

    project__exclude = rest_framework.ModelMultipleChoiceFilter(
        field_name='project',
        queryset=Project.objects.all(),
        exclude=True
    )

    subcontractors_of_package_activity = rest_framework.ModelChoiceFilter(
        queryset=PackageActivity.objects.all(),
        method='filter_by_subcontractors_of_package_activity'
    )

    subcontractors_company = rest_framework.ModelChoiceFilter(
        queryset=Company.objects.all(),
        method='filter_subcontractors_by_company'
    )

    project__key_contacts__exclude_or_company_admins = rest_framework.ModelMultipleChoiceFilter(
        field_name='project',
        queryset=Project.objects.all(),
        method="exclude_project_key_contacts_and_get_company_admins"
    )

    sort = rest_framework.OrderingFilter(
        fields=(
            ('last_name', 'name'),
            ('company__name', 'company'),
            ('group__id', 'group'),
            ('id', 'id'),
        ),
    )

    status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=User.Status.choices,
        widget=QueryArrayWidget
    )

    company = rest_framework.ModelMultipleChoiceFilter(
        field_name='company',
        queryset=Company.all_objects.all(),
        widget=QueryArrayWidget
    )

    exclude_status = rest_framework.MultipleChoiceFilter(
        field_name='status',
        choices=User.Status.choices,
        widget=QueryArrayWidget,
        exclude=True
    )

    def filter_by_subcontractors_of_package_activity(self, queryset, name, value):
        if value:
            filters = {
                'company': OuterRef('company'),
                'package_matrix__package_activity': value
            }

            default_filters = {
                'user': OuterRef('pk')
            }

            if 'project' in self.request.query_params:
                filters['package_matrix__project'] = self.request.query_params['project']
                default_filters['project'] = self.request.query_params['project']

            package_matrix_company_subcontractors_query = queryset.filter(
                Exists(PackageMatrixCompany.objects.filter(**filters)),
                group=User.Group.SUBCONTRACTOR.value)

            if package_matrix_company_subcontractors_query.count() > 0:
                return package_matrix_company_subcontractors_query

            return queryset.filter(Exists(ProjectUser.objects.filter(**default_filters)),
                                   group=User.Group.SUBCONTRACTOR.value)

        return queryset

    def filter_subcontractors_by_company(self, queryset, name, value):
        if value:
            return queryset.filter(
                ~Q(
                    Q(group=User.Group.SUBCONTRACTOR.value) & ~Q(company=value)
                )
            )

        return queryset

    def exclude_project_key_contacts_and_get_company_admins(self, queryset, name, value):
        if len(value) == 0:
            return queryset

        is_company_admin = Q(group_id__in=[User.Group.COMPANY_ADMIN.value])
        is_bound_project = Q(**{name + '__in': value})
        target_project_filter = {'key_contacts': OuterRef('pk'), 'pk__in': [project.pk for project in value]}
        is_not_from_target_project_key_contacts = Q(~Exists(Project.objects.filter(**target_project_filter)))

        return queryset.filter(
            (is_company_admin | is_bound_project) & is_not_from_target_project_key_contacts
        ).distinct()

    def get_by_project_or_company_admins(self, queryset, name, value):
        if len(value) == 0:
            return queryset

        return queryset.filter(
            Q(**{name + '__in': value}) | Q(group_id__in=[User.Group.COMPANY_ADMIN.value])
        ).distinct()

    class Meta:
        model = User
        fields = ('company', 'last_name', 'project')
