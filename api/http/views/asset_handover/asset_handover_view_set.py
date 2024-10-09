from django.db.models import Prefetch
from django_filters import rest_framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.asset_handover.asset_handover_filter import AssetHandoverFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.asset_handover import AssetHandoverUpdateSerializer
from api.http.serializers.asset_handover import AssetHandoverBulkDeleteSerializer
from api.http.serializers.asset_handover.asset_handover_create_serializer import AssetHandoverCreateSerializer
from api.http.serializers.asset_handover.asset_handover_serializer import AssetHandoverSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandover, Project, AssetHandoverDocumentMedia, AssetHandoverStatistics, User
from api.permissions import IsSuperuser, IsManager, IsAdmin, IsCompanyAdmin, IsProjectSubcontractor, IsProjectClient, \
    IsProjectConsultant, IsProjectStaff
from api.queues.send_report import send_csv_report
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import is_expanded, get_int_array_parameter
from api.utilities.tasks_utilities import SerializableRequest


class AssetHandoverViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager),
        'destroy': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager),
        'update': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager),
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager | IsProjectSubcontractor | IsProjectClient | IsProjectConsultant,),
        'bulk_destroy': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
        'generate_csv': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectConsultant | IsProjectSubcontractor | IsProjectClient,),
    }

    serializer_class = AssetHandoverSerializer
    queryset = AssetHandover.objects.all()
    filterset_class = AssetHandoverFilter

    def create(self, request, *args, **kwargs):
        self.serializer_class = AssetHandoverCreateSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_asset_handovers = serializer.create(serializer.validated_data)
        serializer = AssetHandoverSerializer(created_asset_handovers, many=True, expand=[
            'expanded_asset_handover_documents',
            'expanded_location_matrix',
            'expanded_package_activity.expanded_can_add_asset_handovers',
        ], context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def bulk_destroy(self, request, *args, **kwargs):
        serializer = AssetHandoverBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_queryset().filter(**serializer.validated_data).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        self.serializer_class = AssetHandoverUpdateSerializer
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    def generate_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])

        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, AssetHandoverDocumentMedia, project.pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs['project_pk'])
            self.queryset = self.queryset.filter(location_matrix__project_id=project.pk)

        if is_expanded(self.request, 'expanded_asset_handover_documents.expanded_asset_handover_statistics'):
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
            elif self.request.user.is_consultant:
                statistics_filters.update(group=None)
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
                'assethandoverdocument_set__assethandoverstatistics_set',
                queryset=AssetHandoverStatistics.objects.filter(**statistics_filters)
            ))

        return self.queryset
