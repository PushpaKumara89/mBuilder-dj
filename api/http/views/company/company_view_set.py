from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.company.company_filter import CompanyFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import CompanySerializer
from api.http.views.view import BaseViewSet
from api.models import Company
from api.permissions import IsSuperuser, IsCompanyAdmin, IsAdmin, IsManager
from api.queues.send_report import send_csv_report
from api.utilities.helpers import is_expanded
from api.utilities.tasks_utilities import SerializableRequest


class CompanyViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'retrieve': (IsAuthenticated | HasAPIKey,),
        'list': (IsAuthenticated | HasAPIKey,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    filterset_class = CompanyFilter
    search_fields = ['name']

    def get_queryset(self):
        if is_expanded(self.request, 'expanded_users_count'):
            self.queryset = self.queryset.prefetch_related('user_set')

        return self.queryset

    def perform_destroy(self, instance):
        if instance.user_set.filter(deleted__isnull=True, is_active=True).exists():
            raise ValidationError('You cannot delete this company.')
        instance.delete()

    def generate_csv(self, request, *args, **kwargs):
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, Company, None, request.user.email)

        return Response(status=status.HTTP_200_OK)
