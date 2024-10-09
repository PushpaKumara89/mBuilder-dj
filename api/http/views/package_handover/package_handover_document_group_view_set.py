from django_filters import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.mixins import ListModelMixin
from api.http.serializers import PackageHandoverDocumentGroupSerializer
from api.http.views.view import BaseViewSet
from api.models import PackageHandoverDocumentGroup
from api.permissions import IsSuperuser
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_int_array_parameter


class PackageHandoverDocumentGroupViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'retrieve': (IsAuthenticated, IsSuperuser,),
        'list': (IsAuthenticated,),
        'destroy': (IsAuthenticated, IsSuperuser,),
    }

    serializer_class = PackageHandoverDocumentGroupSerializer
    queryset = PackageHandoverDocumentGroup.objects.all()
    search_fields = ['name']

    def get_queryset(self):
        filters = {
            'packagehandoverdocumenttype__packagehandoverdocument__deleted__isnull': True,
            'packagehandoverdocumenttype__packagehandoverdocument__package_handover__deleted__isnull': True
        }

        projects = clean_query_param(
            get_int_array_parameter('project', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )

        if projects:
            filters[('packagehandoverdocumenttype__packagehandoverdocument'
                     '__package_handover__package_matrix__project__in')] = projects

        packages = clean_query_param(
            get_int_array_parameter('package', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )

        if packages:
            filters[('packagehandoverdocumenttype__packagehandoverdocument'
                     '__package_handover__package_matrix__package__in')] = packages

        package_activity = clean_query_param(
            get_int_array_parameter('package_activity', self.request.query_params),
            rest_framework.NumberFilter,
            int
        )

        if package_activity:
            filters[('packagehandoverdocumenttype__packagehandoverdocument'
                     '__package_handover__package_matrix__package_activity__in')] = package_activity

        if self.request.user.is_subcontractor or self.request.user.is_consultant:
            filters['pk__in'] = PackageHandoverDocumentGroup.GROUPS_MAP.get(self.request.user.group.pk)

        return self.queryset.filter(**filters).distinct()
