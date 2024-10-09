from django.db.models import OuterRef, Exists
from django_filters import rest_framework
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters.package_handover_document_type_filter import PackageHandoverDocumentTypeFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.package_handover.package_handover_document import PackageHandoverDocumentTypeSerializer
from api.http.views.view import BaseViewSet
from api.models import PackageHandoverDocumentType, Project, PackageHandoverDocumentGroup, HandoverDocument, \
    PackageHandoverDocumentMedia
from api.permissions import IsSuperuser, IsStaff, IsProjectConsultant, IsProjectSubcontractor, IsProjectClient
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter, get_boolean_query_param, get_int_array_parameter


class PackageHandoverDocumentTypeViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'retrieve': (IsAuthenticated, IsSuperuser | IsStaff,),
        'list': (IsAuthenticated,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'get_for_project': (IsAuthenticated, IsSuperuser | IsStaff | IsProjectConsultant | IsProjectClient | IsProjectSubcontractor,),
    }

    serializer_class = PackageHandoverDocumentTypeSerializer
    queryset = PackageHandoverDocumentType.objects.all()
    filterset_class = PackageHandoverDocumentTypeFilter
    search_fields = ['name']

    def get_for_project(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    def get_queryset(self):
        is_configuration_mode = get_boolean_query_param(self.request.query_params, 'configuration_mode')

        if is_configuration_mode:
            kwfilters = {}
        else:
            kwfilters = {
                'packagehandoverdocument__deleted__isnull': True,
                'packagehandoverdocument__packagehandoverdocumentmedia__deleted__isnull': True
            }

        filters = []
        packages = clean_query_param(
            get_int_array_parameter('package', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )

        package_activity = clean_query_param(
            get_int_array_parameter('package_activity', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )

        if 'has_handover_documents' in self.request.query_params:
            self.__add_filter_by_handover_document(packages, package_activity, filters, self.kwargs['project_pk'])
        else:
            if packages:
                kwfilters['packagehandoverdocument__package_handover__package_matrix__package__in'] = packages

            if package_activity:
                kwfilters['packagehandoverdocument__package_handover__package_matrix__package_activity__in'] = package_activity

            if packages or package_activity:
                kwfilters['packagehandoverdocument__package_handover__deleted__isnull'] = True
                kwfilters['packagehandoverdocument__package_handover__package_matrix__deleted__isnull'] = True

        if self.request.user.is_subcontractor or self.request.user.is_consultant:
            kwfilters['group__pk__in'] = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.request.user.group.pk)

        self.__add_filters_by_project(kwfilters)

        return self.queryset.filter(*filters, **kwfilters).distinct()

    def __add_filters_by_project(self, filters: dict) -> None:
        if 'project_pk' in self.kwargs:
            project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs.get('project_pk'))
            filters['packagehandoverdocument__package_handover__deleted__isnull'] = True
            filters['packagehandoverdocument__package_handover__package_matrix__deleted__isnull'] = True
            filters['packagehandoverdocument__package_handover__package_matrix__project'] = project

            if not self.request.user.is_superuser and not self.request.user.is_multiplex and not self.request.user.is_client:
                filters['group__in'] = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.request.user.group.pk, [])

            if self.request.user.is_subcontractor:
                filters['packagehandoverdocument__package_handover__package_matrix__packagematrixcompany__company'] = self.request.user.company

    def __add_filter_by_handover_document(self, package: list, package_activity: list, filters: list, project_pk: int) -> None:
        handover_document_filters = []
        handover_document_kwfilters = {
            'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
            'document_type': OuterRef('id'),
            'project': self.kwargs['project_pk']
        }

        if package:
            handover_document_kwfilters['package__in'] = package

        if package_activity:
            handover_document_kwfilters['package_activity__in'] = package_activity

        if self.request.user.is_consultant:
            handover_document_kwfilters['company'] = self.request.user.company

        location_matrix_package_kwfilters = {
            'id': OuterRef('entity_id'),
            'deleted__isnull': True,
            'package_handover_document__deleted__isnull': True,
            'package_handover_document__package_handover__deleted__isnull': True,
            'package_handover_document__package_handover__package_matrix__deleted__isnull': True,
            'package_handover_document__package_handover__package_matrix__locationmatrixpackage__deleted__isnull': True,
            'package_handover_document__package_handover__package_matrix__locationmatrixpackage__location_matrix__deleted__isnull': True,
            'package_handover_document__package_handover__package_matrix__locationmatrixpackage__enabled': True,
            'package_handover_document__package_handover__package_matrix__locationmatrixpackage__location_matrix__project': project_pk,
            'package_handover_document__package_handover__package_matrix__project': project_pk,
        }

        building = clean_query_param(
            get_array_parameter('building', self.request.query_params),
            rest_framework.CharFilter
        )

        level = clean_query_param(
            get_array_parameter('level', self.request.query_params),
            rest_framework.CharFilter
        )

        area = clean_query_param(
            get_array_parameter('area', self.request.query_params),
            rest_framework.CharFilter
        )

        if building:
            location_matrix_package_kwfilters['package_handover_document__package_handover'
                                              '__package_matrix__locationmatrixpackage'
                                              '__location_matrix__building__in'] = building

        if level:
            location_matrix_package_kwfilters['package_handover_document__package_handover'
                                              '__package_matrix__locationmatrixpackage'
                                              '__location_matrix__level__in'] = level

        if area:
            location_matrix_package_kwfilters['package_handover_document__package_handover'
                                              '__package_matrix__locationmatrixpackage'
                                              '__location_matrix__area__in'] = area

        if any((building, level, area)):
            handover_document_filters.append(
                Exists(PackageHandoverDocumentMedia.objects.filter(**location_matrix_package_kwfilters)),
            )

        filters.append(
            Exists(HandoverDocument.objects.filter(*handover_document_filters, **handover_document_kwfilters))
        )
