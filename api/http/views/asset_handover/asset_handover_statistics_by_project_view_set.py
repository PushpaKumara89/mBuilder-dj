from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_project_filtered_statistics_read_serializer import \
    AssetHandoverProjectFilteredStatisticsReadSerializer
from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_project_statistics_read_serializer import \
    AssetHandoverProjectStatisticsReadSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, AssetHandoverStatistics
from api.permissions import IsSuperuser, IsCompanyAdmin, IsProjectManager, IsProjectAdmin, IsProjectClient, IsProjectConsultant, IsProjectSubcontractor
from api.services.asset_handover_statistics_service import AssetHandoverStatisticsService


class AssetHandoverStatisticsByProjectViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'get_project_statistics': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),
        'get_filtered_project_statistics': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient),
    }

    serializer_class = AssetHandoverProjectStatisticsReadSerializer
    queryset = AssetHandoverStatistics.objects.all()

    def get_project_statistics(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs['project_pk'])
        statistics = AssetHandoverStatisticsService().aggregate_statistics_by_project(project, request.user)
        serializer = self.get_serializer(statistics)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_filtered_project_statistics(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs['project_pk'])
        statistics = AssetHandoverStatisticsService().aggregate_filtered_statistics_by_project(
            project,
            request.query_params
        )
        serializer = AssetHandoverProjectFilteredStatisticsReadSerializer(statistics)

        return Response(serializer.data, status=status.HTTP_200_OK)
