from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from api.http.filters.handover_document_company_filter import HandoverDocumentCompanyFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import CompanySerializer
from api.http.views.view import BaseViewSet
from api.models import Company
from api.permissions import IsSuperuser, IsCompanyAdmin, IsProjectAdmin, IsProjectManager, IsProjectClient
from api.utilities.handover_document_utilities import add_filters_by_locations, add_document_type_filters
from api.utilities.helpers import is_expanded


class HandoverDocumentsCompanyViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager| IsProjectClient),
    }

    serializer_class = CompanySerializer
    filterset_class = HandoverDocumentCompanyFilter
    queryset = Company.objects.all()
    search_fields = ['name']

    def get_queryset(self):
        filters = []

        self.__apply_handover_document_filters(filters)

        if is_expanded(self.request, 'expanded_users_count'):
            self.queryset = self.queryset.prefetch_related('user_set')

        return self.queryset.filter(*filters).distinct()

    def __apply_handover_document_filters(self, filters: list) -> None:
        if 'has_handover_documents' in self.request.query_params:
            handover_documents_filters = []
            filters_ = HandoverDocumentCompanyFilter().get_filter_kwargs()
            handover_documents_kwfilter = {
                'handoverdocument__project': self.kwargs['project_pk'],
                'handoverdocument__deleted__isnull': True,
                **filters_
            }

            add_document_type_filters(
                request=self.request,
                filters=handover_documents_filters,
                handover_document_path='handoverdocument'
            )

            add_filters_by_locations(
                request=self.request,
                handover_document_filters=handover_documents_filters,
                project_pk=self.kwargs['project_pk'],
                handover_document_path='handoverdocument'
            )
            filters.extend(handover_documents_filters)
            filters.append(Q(**handover_documents_kwfilter))
