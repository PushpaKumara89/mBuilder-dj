import pendulum
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.handover_document_filter import HandoverDocumentFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.handover_document_serializer import HandoverDocumentSerializer
from api.http.views.view import BaseViewSet
from api.models import HandoverDocument, PackageHandoverDocumentType, AssetHandoverDocumentType
from api.permissions import IsProjectUser, IsSuperuser, IsCompanyAdmin, IsProjectAdmin, IsProjectManager, \
    IsProjectClient, IsProjectConsultant
from api.queues.celery.handover_document_archive import initiate_generation_process
from api.queues.send_report import send_csv_report
from api.services.handover_document_service import HandoverDocumentService
from api.utilities.handover_document_utilities import add_document_type_filters, add_filters_by_user_role, \
    add_filters_by_locations
from api.utilities.helpers import is_expanded
from api.utilities.tasks_utilities import SerializableRequest


class HandoverDocumentViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'list': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'generate_csv': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'get_archive': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin
                        | IsProjectManager | IsProjectClient | IsProjectConsultant),
    }

    serializer_class = HandoverDocumentSerializer
    queryset = HandoverDocument.objects.all()
    filterset_class = HandoverDocumentFilter
    service = HandoverDocumentService()
    search_fields = ('filename', 'information', 'uid',)

    def generate_csv(self, request, project_pk, *args, **kwargs):
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, HandoverDocument, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def get_archive(self, request, project_pk, *args, **kwargs):
        initiate_generation_process.delay(project_pk, request.user, pendulum.now())

        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        handover_documents_filters = []
        project_pk = self.kwargs.get('project_pk')

        if project_pk:
            handover_documents_filters.append(Q(project_id=project_pk))

        add_filters_by_user_role(self.request.user, handover_documents_filters, project_pk)
        add_document_type_filters(self.request, handover_documents_filters)
        add_filters_by_locations(self.request, handover_documents_filters, project_pk)

        return self.queryset.filter(*handover_documents_filters)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if is_expanded(request=self.request, key='expanded_document_type'):
            context['package_handover_document_types'] = PackageHandoverDocumentType.objects.all()
            context['asset_handover_document_types'] = AssetHandoverDocumentType.objects.all()

        return context
