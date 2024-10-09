from django.db.models import Q, Prefetch
from django_filters import rest_framework
from pydash import objects, find_index
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.package_handover_document_filter import PackageHandoverDocumentFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import PackageHandoverDocumentSerializer, PackageHandoverSerializer, \
    PackageHandoverDocumentGroupSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, PackageHandover, PackageHandoverDocumentGroup, PackageHandoverDocumentMedia, \
    PackageHandoverStatistics, User
from api.models.package_handover.package_handover_document import PackageHandoverDocument
from api.permissions import IsProjectStaff, IsProjectUser, IsSuperuser
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter, get_unique_objects_from_list, get_int_array_parameter, \
    is_expanded
from api.utilities.package_handover_document_media_utilities import get_consultant_company_filter_query


class PackageHandoverDocumentViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, (IsSuperuser | IsProjectStaff)),
        'partial_update': (IsAuthenticated, (IsSuperuser | IsProjectStaff),),
        'create': (IsAuthenticated, (IsSuperuser | IsProjectStaff),),
        'retrieve': (IsAuthenticated, (IsSuperuser | IsProjectUser),),
        'list_grouped': (IsAuthenticated, (IsSuperuser | IsProjectUser),),
        'list': (IsAuthenticated, (IsSuperuser | IsProjectUser),),
        'destroy': (IsAuthenticated, (IsSuperuser | IsProjectStaff),),
    }

    serializer_class = PackageHandoverDocumentSerializer
    queryset = PackageHandoverDocument.objects.all()
    filterset_class = PackageHandoverDocumentFilter

    def list(self, request, *args, **kwargs):
        self.apply_default_group_filter()
        self.__prefetch_expandable_fields()
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))
        self.queryset = self.queryset.filter(
            package_handover__package_matrix__project__pk=project.pk
        )

        return super().list(request, *args, **kwargs)

    def apply_default_group_filter(self) -> None:
        if self.request.user.is_consultant or self.request.user.is_subcontractor:
            group = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.request.user.group_id)
            self.queryset = self.queryset.filter(package_handover_document_type__group_id__in=group)

    def list_grouped(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['project_pk'])

        query_filters = {'package_handover__package_matrix__project_id': project.pk}
        if self.request.user.is_subcontractor:
            query_filters['package_handover__package_matrix__packagematrixcompany__company'] = self.request.user.company

        self.__prefetch_expandable_fields()

        queryset = self.filter_queryset(self.queryset.select_related(
            'package_handover__package_matrix__package_activity', 'package_handover__package_matrix__package',
            'package_handover_document_type__group'
        ).filter(**query_filters))

        page = self.paginate_queryset(queryset)
        package_handovers_data = self.__set_document_groups(
            list(queryset) if page is None else page,
            clean_query_param(
                get_array_parameter('expand', request.query_params),
                rest_framework.CharFilter
            )
        )

        return self.get_paginated_response(package_handovers_data) \
            if page is not None \
            else Response(data=package_handovers_data)

    def __set_document_groups(self, package_handover_documents, expand):
        def filter_package_handover(ph):
            return list(filter(lambda group: group['package_handover_documents'], ph['package_handover_document_groups']))

        def filter_docs(doc):
            return doc.package_handover_document_type.group_id == group_data['id'] and \
                   doc.package_handover_id == package_handover['id']

        document_groups = self.__get_document_groups()
        package_handovers = self.__get_package_handovers(package_handover_documents)

        for package_handover in package_handovers:
            package_handover['package_handover_document_groups'] = objects.clone_deep(document_groups)

            for group_data in package_handover['package_handover_document_groups']:
                docs = list(filter(filter_docs, package_handover_documents))

                group_data['package_handover_documents'] = PackageHandoverDocumentSerializer(
                    docs,
                    many=True,
                    expand=expand,
                    context=self.get_serializer_context()
                ).data

        if self.request.query_params.get('show_all_groups', False):
            return package_handovers

        package_handovers = list(filter(filter_package_handover, package_handovers))
        # Remove from response package handovers without documents.
        for package_handover in package_handovers:
            package_handover['package_handover_document_groups'] = list(
                filter(lambda group: group['package_handover_documents'],
                       package_handover['package_handover_document_groups'])
            )

        status_filter = clean_query_param(
            get_array_parameter('status', self.request.query_params),
            rest_framework.CharFilter
        )

        if status_filter:
            for package_handover in package_handovers:
                for group in package_handover['package_handover_document_groups']:
                    for doc in group['package_handover_documents']:
                        doc['expanded_package_handover_document_media'] = list(
                            filter(lambda media: media['status'] in status_filter,
                                   doc['expanded_package_handover_document_media'])
                        )

        if self.request.user.is_consultant:
            user = self.request.user
            available_media_ids = self.__get_available_media_ids_for_consultant(user)

            for package_handover in package_handovers:
                for group in package_handover['package_handover_document_groups']:
                    for doc in group['package_handover_documents']:
                        doc['expanded_package_handover_document_media'] = list(
                            filter(lambda media: self.__is_available_for_consultant(media['id'], available_media_ids), doc['expanded_package_handover_document_media'])
                        )

        return package_handovers

    def __get_package_handovers(self, docs):
        # For configurations, we need to display all asset handovers,
        # regardless of the presence of the corresponding documents.
        if self.request.query_params.get('show_all_groups', False):
            filters = {
                'package_matrix__project_id': self.kwargs['project_pk']
            }

            package_filter = clean_query_param(
                get_int_array_parameter('package', self.request.query_params),
                rest_framework.NumberFilter,
                int
            )

            package_activity_filter = clean_query_param(
                get_int_array_parameter('package_activity', self.request.query_params),
                rest_framework.NumberFilter,
                int
            )

            if package_filter:
                filters['package_matrix__package_id__in'] = package_filter

            if package_activity_filter:
                filters['package_matrix__package_activity_id__in'] = package_activity_filter

            package_handovers = PackageHandover.objects.select_related('package_matrix').filter(**filters)
        else:
            package_handovers = list(map(lambda doc: doc.package_handover, docs))
            package_handovers = get_unique_objects_from_list(package_handovers)

        return PackageHandoverSerializer(package_handovers, many=True, expand=['expanded_package_activity']).data

    def __get_document_groups(self):
        document_groups_filter = clean_query_param(
            get_int_array_parameter('show_document_group', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )
        document_groups_filter = {'pk__in': document_groups_filter} if document_groups_filter else {}
        document_groups_query = PackageHandoverDocumentGroup.objects.filter(**document_groups_filter).all()

        return PackageHandoverDocumentGroupSerializer(document_groups_query, many=True).data

    def __get_available_media_ids_for_consultant(self, user):
        filters = [
            Q(package_handover_document__package_handover__package_matrix__project_id=self.kwargs['project_pk']),
            get_consultant_company_filter_query(user)
        ]

        return list(PackageHandoverDocumentMedia.objects.filter(*filters).all().values_list('id', flat=True))

    def __is_available_for_consultant(self, package_handover_document_media_id, available_media_ids):
        return find_index(
                available_media_ids,
                lambda media_id: media_id == package_handover_document_media_id
            ) != -1

    def __prefetch_expandable_fields(self):
        if is_expanded(self.request, 'expanded_package_handover_statistics'):
            statistics_filters = {
                'company': None,
            }

            if self.request.user.is_multiplex or self.request.user.is_client:
                statistics_filters['group'] = None
                company = clean_query_param(
                    get_int_array_parameter('company', self.request.query_params),
                    rest_framework.NumberFilter,
                    int
                )

                if company:
                    del statistics_filters['company']
                    del statistics_filters['group']
                    statistics_filters['company_id__in'] = company
                    statistics_filters['group_id__isnull'] = False
            else:
                statistics_filters.update(
                    company=self.request.user.company_id,
                    group_id__in=[
                        self.request.user.group_id,
                        User.Group.COMPANY_ADMIN.value,
                        User.Group.ADMIN.value,
                        User.Group.MANAGER.value,
                    ],
                )

            self.queryset = self.queryset.prefetch_related(Prefetch(
                'packagehandoverstatistics_set',
                queryset=PackageHandoverStatistics.objects.filter(**statistics_filters)
            ))
