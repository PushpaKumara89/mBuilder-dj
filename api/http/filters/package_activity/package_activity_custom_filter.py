from django.db.models import Prefetch, OuterRef, Exists, Q, F
from django.db.models.expressions import RawSQL
from django_filters import rest_framework
from rest_framework.request import Request

from api.models import AssetHandover, PackageMatrix, HandoverDocument, PackageMatrixCompany, \
    PackageHandoverDocumentGroup, LocationMatrixPackage
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import is_expanded, get_array_parameter, get_boolean_query_param, get_int_array_parameter


class PackageActivityCustomFilter:
    def __init__(self, request: Request) -> None:
        self.user = request.user
        self.query_params = request.query_params
        self._request = request
        self.prefetch_related: list[Prefetch] = []
        self.select_related: list[str] = []
        self._filter_args: list = []
        self.filter_kwargs: dict = {}
        self.location_matrix_package_filters: dict = {}

    @property
    def filter_args(self):
        if self.location_matrix_package_filters:
            self._filter_args.append(
                Exists(LocationMatrixPackage.objects.filter(**self.location_matrix_package_filters))
            )

        return self._filter_args

    def add_handover_document(self):
        project_filter = clean_query_param(
            get_int_array_parameter('project', self.query_params),
            rest_framework.NumberFilter,
            int
        )

        package_filter = clean_query_param(
            get_int_array_parameter('package', self.query_params),
            rest_framework.NumberFilter,
            int
        )

        building_filter = clean_query_param(
            get_array_parameter('building', self.query_params),
            rest_framework.CharFilter
        )

        level_filter = clean_query_param(
            get_array_parameter('level', self.query_params),
            rest_framework.CharFilter
        )

        area_filter = clean_query_param(
            get_array_parameter('area', self.query_params),
            rest_framework.CharFilter
        )

        filter_by_company = get_boolean_query_param(self.query_params, 'filter_by_company')
        user_company = self.user.company

        handover_document_filter_args = []
        handover_document_filter_kwargs = {
            'package_activity_id': OuterRef('id'),
            'deleted__isnull': True
        }

        if self.user.is_consultant:
            handover_document_filter_args.append(
                Q(Q(company=user_company, entity=HandoverDocument.Entities.PACKAGE_HANDOVER)
                  | Q(entity=HandoverDocument.Entities.ASSET_HANDOVER))
            )

        if self.user.is_subcontractor:
            handover_document_filter_args.append(
                Exists(PackageMatrixCompany.objects.filter(
                    package_matrix__package_id=OuterRef('package_id'),
                    package_matrix__package_activity_id=OuterRef('package_activity_id'),
                    package_matrix__project_id__in=project_filter,
                    company_id=user_company,
                    deleted__isnull=True
                ))
            )

        if project_filter:
            handover_document_filter_kwargs['project_id__in'] = project_filter

        if any((building_filter, level_filter, area_filter)):
            location_filter_kwargs = {}
            if building_filter:
                location_filter_kwargs['building__in'] = building_filter

            if level_filter:
                location_filter_kwargs['level__in'] = level_filter

            if area_filter:
                location_filter_kwargs['area__in'] = area_filter

            handover_document_filter_args.append(
                Q(Q(entity=HandoverDocument.Entities.ASSET_HANDOVER, **location_filter_kwargs)
                  | Q(entity=HandoverDocument.Entities.PACKAGE_HANDOVER))
            )

        if package_filter:
            handover_document_filter_kwargs['package_id__in'] = package_filter

        if filter_by_company and self.user.is_subcontractor:
            handover_document_filter_kwargs['company_id'] = user_company

        self._filter_args.append(
            Exists(HandoverDocument.objects.filter(*handover_document_filter_args, **handover_document_filter_kwargs))
        )

    def add_base_queryset_filter(self):
        project_filter = clean_query_param(
            get_int_array_parameter('project', self.query_params),
            rest_framework.NumberFilter,
            int
        )

        package_filter = clean_query_param(
            get_int_array_parameter('package', self.query_params),
            rest_framework.NumberFilter,
            int
        )

        building_filter = clean_query_param(
            get_array_parameter('building', self.query_params),
            rest_framework.CharFilter
        )

        level_filter = clean_query_param(
            get_array_parameter('level', self.query_params),
            rest_framework.CharFilter
        )

        area_filter = clean_query_param(
            get_array_parameter('area', self.query_params),
            rest_framework.CharFilter
        )

        package_handover_document_type_filter = clean_query_param(
            get_int_array_parameter('document_type', self.query_params),
            rest_framework.CharFilter,
            int
        )

        filter_by_company = get_boolean_query_param(self.query_params, 'filter_by_company')

        self.add_has_published_tasks()

        if project_filter:
            self.filter_kwargs.update(
                packagematrix__project_id__in=project_filter
            )
            self.location_matrix_package_filters.update(
                package_matrix=RawSQL('package_matrix.id', ()),
            )

        if package_filter:
            self.location_matrix_package_filters.update(
                package_matrix=RawSQL('package_matrix.id', ()),
                package_id__in=package_filter,
            )

        if building_filter:
            self.location_matrix_package_filters.update(
                package_matrix=RawSQL('package_matrix.id', ()),
                location_matrix__building__in=building_filter
            )

        if level_filter:
            self.location_matrix_package_filters.update(
                package_matrix=RawSQL('package_matrix.id', ()),
                location_matrix__level__in=level_filter
            )

        if area_filter:
            self.location_matrix_package_filters.update(
                package_matrix=RawSQL('package_matrix.id', ()),
                location_matrix__area__in=area_filter
            )

        if package_handover_document_type_filter:
            self.filter_kwargs.update(
                packagematrix__packagehandover__packagehandoverdocument__package_handover_document_type__in=package_handover_document_type_filter,
                packagematrix__packagehandover__deleted__isnull=True,
                packagematrix__packagehandover__packagehandoverdocument__deleted__isnull=True,
            )

        if filter_by_company and self.user.is_subcontractor:
            self.filter_kwargs.update(
                packagematrix__packagematrixcompany__company_id=self.user.company_id
            )

        self.add_has_package_handover_documents(project_filter)
        self.add_has_asset_handovers(project_filter)
        self.add_expandable_fields(building_filter, level_filter, area_filter, project_filter, package_filter)

        if self.location_matrix_package_filters:
            self.filter_kwargs.update(
                packagematrix__isnull=False
            )
            self.location_matrix_package_filters.update(
                deleted__isnull=True
            )

        if any((building_filter, level_filter, area_filter)):
            self.location_matrix_package_filters.update(
                location_matrix__deleted__isnull=True,
            )

    def add_has_published_tasks(self):
        if 'has_published_tasks' in self.query_params:
            has_published_tasks = get_boolean_query_param(self.query_params, 'has_published_tasks')
            self.location_matrix_package_filters.update(
                enabled=has_published_tasks,
            )

    def add_has_package_handover_documents(self, project_filter):
        if 'has_package_handover_documents' in self.query_params:
            has_package_handover_documents = get_boolean_query_param(self.query_params, 'has_package_handover_documents')
            package_handover_documents_filters = {
                'project_id__in': project_filter,
                'package_activity_id': OuterRef('id'),
                'packagehandover__deleted__isnull': True,
                'packagehandover__packagehandoverdocument__deleted__isnull': True,
                'packagehandover__packagehandoverdocument__isnull': not has_package_handover_documents,
            }

            if self.user.is_subcontractor or self.user.is_consultant:
                package_handover_documents_filters[
                    'packagehandover__packagehandoverdocument__package_handover_document_type__group__pk__in'] \
                    = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.user.group.pk)

            self._filter_args.append(Exists(PackageMatrix.objects.filter(**package_handover_documents_filters)))

    def add_has_asset_handovers(self, project_filter):
        if self.query_params.get('has_asset_handovers') is not None:
            asset_handover_filters = {
                'project_id__in': project_filter,
                'package_activity_id': OuterRef('id')
            }

            if self.query_params.get('with_deleted_asset_handovers') is None:
                asset_handover_filters['deleted__isnull'] = True

            if self.user.is_subcontractor:
                asset_handover_filters = {
                    **asset_handover_filters,
                    'package_activity__packagematrix__project_id__in': project_filter,
                    'package_activity__packagematrix__deleted__isnull': True,
                    'package_activity__packagematrix__packagematrixcompany__company': self.user.company
                }

            self._filter_args.append(Exists(AssetHandover.objects.filter(**asset_handover_filters)))

    def add_expandable_fields(self,
                              building_filter: list,
                              level_filter: list,
                              area_filter: list,
                              project_filter: list,
                              package_ids: list[int]):
        if is_expanded(self._request, 'expanded_projects_count'):
            self.prefetch_related.append(
                Prefetch('packagematrix_set',
                         queryset=PackageMatrix.objects.filter(
                             deleted__isnull=True,
                             package__deleted__isnull=True,
                             project__deleted__isnull=True
                         ),
                         to_attr='not_deleted_packagematrix_set'
                         )
            )

        if is_expanded(self._request, 'expanded_can_add_asset_handovers'):
            self.prefetch_related.append(
                Prefetch('locationmatrixpackage_set',
                         queryset=LocationMatrixPackage.objects.filter(
                             enabled=True,
                             deleted__isnull=True,
                             location_matrix__project_id=self.query_params.get('project'),
                             location_matrix__deleted__isnull=True
                         ),
                         to_attr='enabled_location_matrix_packages'
                         )
            )

            self.prefetch_related.append(
                Prefetch('assethandover_set',
                         queryset=AssetHandover.objects.filter(
                             location_matrix__project_id=self.query_params.get('project'),
                             location_matrix__deleted__isnull=True,
                             location_matrix__locationmatrixpackage__package_activity_id=F('package_activity_id'),
                             location_matrix__locationmatrixpackage__enabled=True,
                             location_matrix__locationmatrixpackage__deleted__isnull=True
                         ),
                         to_attr='asset_handovers'
                         )
            )

        if is_expanded(self._request, 'expanded_files'):
            self.prefetch_related.append(Prefetch('files'))

        if is_expanded(self._request, 'expanded_package_handover'):
            self.prefetch_related.append(
                Prefetch('packagematrix_set',
                         queryset=PackageMatrix.objects.prefetch_related('packagehandover_set').filter(
                             project__in=project_filter,
                             deleted__isnull=True))
            )

        if is_expanded(self._request, 'expanded_asset_handover_statistics'):
            id_filter = get_int_array_parameter('id', self.query_params)
            asset_handover_filters = {
                'location_matrix__project_id__in': project_filter,
            }

            if package_ids:
                asset_handover_filters = {
                    'package_activity__packagematrix__deleted__isnull': True,
                    'package_activity__packagematrix__package_id__in': package_ids,
                    'package_activity__packagematrix__project_id__in': project_filter,
                    **asset_handover_filters
                }

            if building_filter:
                asset_handover_filters['location_matrix__building__in'] = building_filter

            if level_filter:
                asset_handover_filters['location_matrix__level__in'] = level_filter

            if area_filter:
                asset_handover_filters['location_matrix__area__in'] = area_filter

            if id_filter:
                asset_handover_filters['package_activity_id__in'] = id_filter

            self.prefetch_related.append(
                Prefetch('assethandover_set', queryset=AssetHandover.objects.filter(**asset_handover_filters))
            )
