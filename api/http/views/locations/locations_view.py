from django.db.models import Q, Exists, OuterRef
from django.db.models.expressions import RawSQL, Value
from django_filters import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters import LocationsFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.views.view import BaseViewSet
from api.models import LocationMatrix, AssetHandover, HandoverDocument, PackageMatrixCompany
from api.permissions import IsSuperuser, IsProjectClient, IsProjectConsultant, IsProjectSubcontractor
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_boolean_query_param, get_int_array_parameter


class LocationsView(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (
            HasAPIKey
            | PermissionGroup(
                IsAuthenticated,
                IsSuperuser
                | IsProjectStaff
                | IsProjectClient
                | IsProjectConsultant
                | IsProjectSubcontractor
            ),
        ),
    }

    queryset = LocationMatrix.objects.all()
    serializer_class = LocationMatrixSerializer
    filterset_class = LocationsFilter

    def get_queryset(self):
        if 'with_deleted' in self.request.query_params:
            return LocationMatrix.all_objects.all()
        return self.queryset

    def _get_locations_filters(self, use_raw_values=False) -> tuple:
        query_params = self.request.query_params
        package_ids = clean_query_param(
            get_int_array_parameter('package', query_params),
            rest_framework.NumberFilter,
            int
        )
        package_activity_ids = clean_query_param(
            get_int_array_parameter('package_activity', query_params),
            rest_framework.NumberFilter,
            int
        )
        project = self.kwargs['project_pk']
        kwfilters = {'project': project, 'deleted__isnull': True}
        filters = []

        if 'has_published_tasks' in query_params:
            kwfilters.update(
                locationmatrixpackage__deleted__isnull=True,
                locationmatrixpackage__enabled=get_boolean_query_param(query_params, 'has_published_tasks')
            )

        if package_ids:
            kwfilters.update(
                locationmatrixpackage__deleted__isnull=True,
                locationmatrixpackage__package_id__in=package_ids,
            )

        if package_activity_ids:
            kwfilters.update(
                locationmatrixpackage__deleted__isnull=True,
                locationmatrixpackage__package_activity_id__in=package_activity_ids
            )

        if query_params.get('has_handover_documents', False):
            kwfilters.update(
                locationmatrixpackage__enabled=True,
                locationmatrixpackage__deleted__isnull=True,
            )
            handover_documents_filters = [
                Q(
                    building=OuterRef('building'),
                    level=OuterRef('level'),
                    area=OuterRef('area'),
                    entity=Value(f'{HandoverDocument.Entities.ASSET_HANDOVER}') if use_raw_values else HandoverDocument.Entities.ASSET_HANDOVER
                )
                | Q(
                    package=RawSQL('location_matrix_packages.package_id', ()),
                    package_activity=RawSQL('location_matrix_packages.package_activity_id', ()),
                    entity=Value(f'{HandoverDocument.Entities.PACKAGE_HANDOVER}') if use_raw_values else HandoverDocument.Entities.PACKAGE_HANDOVER
                )
            ]

            handover_documents_kwfilters = {
                'project': project,
                'deleted__isnull': True
            }

            if self.request.user.is_consultant:
                handover_documents_filters.append(
                    Q(
                        company=Value(f'{self.request.user.company_id}') if use_raw_values else self.request.user.company_id,
                        entity=Value(f'{HandoverDocument.Entities.PACKAGE_HANDOVER}') if use_raw_values else HandoverDocument.Entities.PACKAGE_HANDOVER
                    ) |
                    Q(
                        entity=Value(f'{HandoverDocument.Entities.ASSET_HANDOVER}') if use_raw_values else HandoverDocument.Entities.ASSET_HANDOVER
                    )
                )

            if self.request.user.is_subcontractor:
                handover_documents_kwfilters.update(company=self.request.user.company_id)
                handover_documents_filters.append(
                    Exists(PackageMatrixCompany.objects.filter(
                        package_matrix__package=OuterRef('package'),
                        package_matrix__package_activity=OuterRef('package_activity'),
                        package_matrix__project=project,
                        company=self.request.user.company_id,
                        deleted__isnull=True
                    ))
                )

            filters.append(
                Exists(HandoverDocument.objects.filter(
                    *handover_documents_filters,
                    **handover_documents_kwfilters
                ))
            )

        if query_params.get('exclude_where_asset_handover_exist', False):
            asset_handover_filters = {
                'location_matrix__project_id': self.kwargs['project_pk'],
                'location_matrix_id': OuterRef('id'),
                'deleted': None
            }
            if package_activity_ids:
                asset_handover_filters['package_activity_id__in'] = package_activity_ids

            package_activity_has_only_deleted_asset_handovers = ~Exists(AssetHandover.objects.filter(**asset_handover_filters))
            filters.append(Q(Q(assethandover__isnull=True) | package_activity_has_only_deleted_asset_handovers))

        return filters, kwfilters
