from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.package_handover.package_handover_statistics.package_handover_statistics_read_serializer import \
    PackageHandoverStatisticsReadSerializer
from api.http.views.view import BaseViewSet
from api.models import Project
from api.models.package_handover import PackageHandover
from api.permissions import IsSuperuser, IsProjectAdmin, IsProjectManager, IsProjectClient, IsProjectConsultant, IsProjectSubcontractor
from api.services.package_handover_statistics_service import PackageHandoverStatisticsService


class PackageHandoverStatisticsViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'get_status_counter': (IsAuthenticated, (IsSuperuser | IsProjectAdmin | IsProjectManager | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
    }

    serializer_class = PackageHandoverStatisticsReadSerializer
    queryset = PackageHandover.objects.all()

    def get_status_counter(self, request, project_pk, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=project_pk)
        status_counter = PackageHandoverStatisticsService().aggregate_status_counter_for_project(project, request.user)
        response_data = self.get_serializer(status_counter).data
        return Response(data=response_data, status=status.HTTP_200_OK)
