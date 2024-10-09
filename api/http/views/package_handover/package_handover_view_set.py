from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.package_handover_filter import PackageHandoverFilter
from api.http.serializers import PackageHandoverSerializer, PackageHandoverRestrictedUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, PackageHandoverDocumentMedia
from api.models.package_handover import PackageHandover
from api.permissions import IsSuperuser, IsProjectStaff, IsProjectConsultant, IsProjectSubcontractor, \
    DoesProjectSubcontractorCanUpdate, IsProjectClient
from api.queues.send_report import send_csv_report
from api.utilities.tasks_utilities import SerializableRequest


class PackageHandoverViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, (IsSuperuser | IsProjectStaff | DoesProjectSubcontractorCanUpdate),),
        'partial_update': (IsAuthenticated, (IsSuperuser | IsProjectStaff),),
        'generate_csv': (IsAuthenticated, (IsSuperuser | IsProjectStaff | IsProjectConsultant | IsProjectSubcontractor | IsProjectClient),),
    }

    filterset_class = PackageHandoverFilter
    serializer_class = PackageHandoverSerializer
    queryset = PackageHandover.objects.all()

    def update(self, request, *args, **kwargs):
        self.serializer_class = PackageHandoverRestrictedUpdateSerializer

        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(package_matrix__project__pk=self.kwargs['project_pk'])

        if self.request.user.is_subcontractor:
            self.queryset = self.queryset.filter(
                package_matrix__packagematrixcompany__company=self.request.user.company)

        return self.queryset

    def generate_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])

        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, PackageHandoverDocumentMedia, project.pk, request.user.email)

        return Response(status=status.HTTP_200_OK)
