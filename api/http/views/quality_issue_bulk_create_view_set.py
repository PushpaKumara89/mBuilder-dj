from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers import QualityIssueSerializer
from api.http.serializers.quality_issue.quality_issue_bulk_create_serializer import QualityIssueBulkCreateSerializer
from api.http.views.view import BaseViewSet
from api.models import QualityIssue, Project
from api.permissions import IsSuperuser, IsProjectClient
from api.permissions.is_project_consultant import IsProjectConsultant
from api.services.quality_issue_entity_service import QualityIssueEntityService


class QualityIssueBulkCreateViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'bulk_create': (IsAuthenticated, IsSuperuser | IsProjectClient | IsProjectConsultant,)
    }

    serializer_class = QualityIssueBulkCreateSerializer
    service = QualityIssueEntityService()
    queryset = QualityIssue.objects.all()

    def bulk_create(self, request, project_pk, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=project_pk)
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_quality_issues = self.service.bulk_create(project, serializer.validated_data, user=request.user)
        response_data = QualityIssueSerializer(created_quality_issues, many=True).data

        return Response(data=response_data, status=status.HTTP_200_OK)
