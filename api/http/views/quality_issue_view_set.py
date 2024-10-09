from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.quality_issue.quality_issue_filter import QualityIssueFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.quality_issue.quality_issue_count_serializer import QualityIssueCountSerializer
from api.http.serializers.quality_issue.quality_issue_serializer import QualityIssueSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.http.views.view import BaseViewSet
from api.models import QualityIssue
from api.permissions import IsSuperuser, IsProjectClient, IsProjectUser, IsProjectStaff
from api.permissions.is_project_consultant import IsProjectConsultant
from api.permissions.permission_group import PermissionGroup
from api.queues.send_report import send_csv_report, send_pdf_report
from api.services.quality_issue_entity_service import QualityIssueEntityService
from api.utilities.helpers import is_expanded
from api.utilities.quality_issue_utilities import apply_default_queryset_filters
from api.utilities.tasks_utilities import SerializableRequest


class QualityIssueViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser | IsProjectUser),
        'partial_update': (IsAuthenticated, IsSuperuser | IsProjectUser,),
        'create': (IsAuthenticated, IsSuperuser | IsProjectClient | IsProjectConsultant,),
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant, ),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'creators': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant, ),),
        'count': (IsAuthenticated, IsSuperuser | IsProjectUser,),
        'generate_csv': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant,),
        'generate_pdf': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant,)
    }

    serializer_class = QualityIssueSerializer
    service = QualityIssueEntityService()
    queryset = QualityIssue.objects.all()
    filterset_class = QualityIssueFilter
    search_fields = ['user__last_name', 'user__first_name', 'user__email',
                     'location_matrix__building', 'location_matrix__area',
                     'location_matrix__level', 'id', 'description',
                     'qualityissueupdate__recipients__email',
                     'qualityissueupdate__recipients__first_name',
                     'qualityissueupdate__recipients__last_name']

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.create(serializer.validated_data, user=request.user)

        return Response(data=self.get_serializer(result).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        self.queryset = apply_default_queryset_filters(self.kwargs, self.queryset, self.request)
        self.queryset = self.queryset.default_order(self.request.user, self.request.query_params)

        if is_expanded(self.request, 'expanded_location_matrix'):
            self.queryset = self.queryset.select_related('location_matrix')

        if is_expanded(self.request, 'expanded_user'):
            self.queryset = self.queryset.select_related('user')

        if is_expanded(self.request, 'expanded_attachments'):
            self.queryset = self.queryset.prefetch_related('attachments')

        if is_expanded(self.request, 'expanded_user.expanded_user_company'):
            self.queryset = self.queryset.select_related('user__company')

        if is_expanded(self.request, 'expanded_subtasks'):
            self.queryset = self.queryset.prefetch_related('subtask_set__files')

        if is_expanded(self.request, 'expanded_response_category'):
            self.queryset = self.queryset.select_related('response_category')

        return self.queryset

    def creators(self, request, *args, **kwargs):
        quality_issues = self.filter_queryset(self.get_queryset().order_by('user_id')).select_related('user').distinct('user__pk')

        users = [quality_issue.user for quality_issue in quality_issues]
        serializer = UserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def count(self, request, *args, **kwargs):
        total_all = self.filter_queryset(self.get_queryset()).count()
        statuses_count = {quality_issue_status: 0 for quality_issue_status in QualityIssue.Status.values}

        if total_all > 0:
            quality_issues = self.filter_queryset(self.get_queryset()).values('status')

            for quality_issue in quality_issues:
                statuses_count[quality_issue['status']] += 1

        serializer = QualityIssueCountSerializer({
            'total': total_all,
            **statuses_count
        })

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def generate_csv(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, QualityIssue, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def generate_pdf(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_pdf_report(serializable_request, QualityIssue, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)
