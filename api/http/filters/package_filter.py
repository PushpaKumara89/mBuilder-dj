from django.db.models import OuterRef, Exists, Q
from django_filters import rest_framework
from rest_framework.request import Request
from typing import Optional, Union, List, Dict

from api.models import Package, Project, PackageHandoverDocumentGroup, PackageMatrix, AssetHandover, HandoverDocument, \
    PackageMatrixCompany, LocationMatrixPackage
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.handover_document_utilities import add_filters_by_locations
from api.utilities.helpers import get_boolean_query_param, get_array_parameter, get_int_array_parameter


class PackageFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('order', 'order'),
        ),
    )

    exclude_bound_with_project = rest_framework.ModelMultipleChoiceFilter(
        field_name='projects',
        queryset=Project.objects.all(),
        exclude=True
    )

    class Meta:
        model = Package
        fields = ('order',)


class PackageCustomPackageMatrixFilter:
    def __init__(self, request: Request, project_pk: Optional[Union[int, str]]) -> None:
        self.user = request.user
        self.query_params = request.query_params
        self._request = request
        self.project_pk = clean_query_param(project_pk, rest_framework.NumberFilter, int)
        self._filter_args: List = []
        self.filter_kwargs: Dict = {}
        self.location_matrix_package_filters = {}

    @property
    def filter_args(self):
        if self.location_matrix_package_filters:
            self._filter_args.append(Exists(LocationMatrixPackage.objects.filter(**self.location_matrix_package_filters)))
        return self._filter_args

    def add_filter_by_company(self) -> None:
        if get_boolean_query_param(self.query_params, 'filter_by_company') and self.user.is_subcontractor:
            self.filter_kwargs['packagematrix__project'] = self.project_pk
            self.location_matrix_package_filters.update(
                package=OuterRef('id'),
                package_matrix__packagematrixcompany__company_id=self.user.company_id,
                package_matrix__packagematrixcompany__deleted__isnull=True,
                package_matrix__deleted__isnull=True
            )

    def add_location_filters(self) -> None:
        if not get_boolean_query_param(self.query_params, 'has_handover_documents'):
            locations = ['building', 'level', 'area']
            location_matrix_package_filters = {}

            for location in locations:
                if filter_value := get_array_parameter(location, self.query_params):
                    cleaned_values = clean_query_param(filter_value, rest_framework.CharFilter)
                    location_matrix_package_filters['location_matrix__%s__in' % location] = cleaned_values

            if location_matrix_package_filters:
                self.location_matrix_package_filters.update(
                    package_id=OuterRef('id'),
                    deleted__isnull=False,
                    **location_matrix_package_filters
                )

    def add_package_handover_filters(self) -> None:
        if 'has_package_handover_documents' in self.query_params:
            has_package_handover_documents = get_boolean_query_param(self.query_params, 'has_package_handover_documents')
            package_handover_documents_filters = {
                'project_id': self.project_pk,
                'package_id': OuterRef('id'),
                'packagehandover__deleted__isnull': True,
                'packagehandover__packagehandoverdocument__isnull': not has_package_handover_documents,
                'packagehandover__packagehandoverdocument__deleted__isnull': True,
            }

            if self.user.is_subcontractor or self.user.is_consultant:
                filter_name = 'packagehandover__packagehandoverdocument__package_handover_document_type__group__pk__in'
                filter_value = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.user.group.pk)
                package_handover_documents_filters[filter_name] = filter_value

            subquery = Exists(PackageMatrix.objects.filter(**package_handover_documents_filters))
            self.filter_args.append(subquery)

        if filter_value := get_int_array_parameter('document_type', self.query_params):
            cleaned_values = clean_query_param(filter_value, rest_framework.NumberFilter)

            self.location_matrix_package_filters.update(
                package=OuterRef('id'),
                deleted__isnull=True,
                package_matrix__deleted__isnull=True,
                package_matrix__packagehandover__deleted__isnull=True,
                package_matrix__packagehandover__packagehandoverdocument__deleted__isnull=True,
                package_matrix__packagehandover__packagehandoverdocument__package_handover_document_type__in=cleaned_values
            )

    def add_asset_handover_filters(self) -> None:
        if 'has_asset_handovers' in self.query_params:
            asset_handover_filters = {
                'project_id': self.project_pk,
                'project__packagematrix__package_id': OuterRef('id'),
                'project__packagematrix__deleted__isnull': True,
            }

            if self.query_params.get('with_deleted_asset_handovers') is None:
                asset_handover_filters['deleted__isnull'] = True

            if self.user.is_subcontractor:
                asset_handover_filters = {
                    **asset_handover_filters,
                    'project__packagematrix__packagematrixcompany__company': self.user.company
                }

            self.filter_args.append(Exists(AssetHandover.objects.filter(**asset_handover_filters)))

    def add_tasks_filters(self) -> None:
        has_published_tasks = get_boolean_query_param(self.query_params, 'has_published_tasks', True)

        self.filter_kwargs['packagematrix__project'] = self.project_pk
        self.filter_kwargs['packagematrix__deleted__isnull'] = True
        self.location_matrix_package_filters.update(
            package_id=OuterRef('id'),
            deleted__isnull=True,
            enabled=has_published_tasks,
        )

    def add_handover_document_filters(self) -> None:
        if 'has_handover_documents' in self.query_params:
            user_company_id = self.user.company_id
            handover_document_filters = []
            handover_document_kwfilters = {
                'package_id': OuterRef('id'),
                'deleted__isnull': True,
                'project_id': self.project_pk
            }

            if self.user.is_consultant:
                handover_document_filters.append(
                    Q(Q(company_id=user_company_id, entity=HandoverDocument.Entities.PACKAGE_HANDOVER)
                      | Q(entity=HandoverDocument.Entities.ASSET_HANDOVER))
                )

            if self.user.is_subcontractor:
                handover_document_kwfilters['company_id'] = user_company_id
                handover_document_filters.append(
                    Exists(PackageMatrixCompany.objects.filter(
                        package_matrix__package_id=OuterRef('package_id'),
                        package_matrix__package_activity_id=OuterRef('package_activity_id'),
                        package_matrix__project_id=self.project_pk,
                        package_matrix__deleted__isnull=True,
                        company_id=user_company_id,
                        deleted__isnull=True
                    ))
                )

            add_filters_by_locations(self._request, handover_document_filters, self.project_pk)

            self.filter_args.append(Exists(HandoverDocument.objects.filter(
                *handover_document_filters,
                **handover_document_kwfilters
            )))
