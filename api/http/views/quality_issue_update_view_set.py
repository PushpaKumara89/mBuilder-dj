from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.quality_issue_update_filter import QualityIssueUpdateFilter
from rest_framework import mixins, status

from api.http.mixins import ListModelMixin
from api.http.serializers import QualityIssueUpdateSerializer
from api.http.views.view import BaseViewSet
from api.models import QualityIssueUpdate, QualityIssue
from api.permissions import IsSuperuser, IsProjectClient, IsProjectConsultant, IsProjectStaff
from api.permissions.permission_group import PermissionGroup
from api.services.quality_issue_update_entity_service import QualityIssueUpdateEntityService


class QualityIssueUpdateViewSet(BaseViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, ListModelMixin):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant, ),),
        'create': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant, ),),
    }
    serializer_class = QualityIssueUpdateSerializer
    service = QualityIssueUpdateEntityService()
    filterset_class = QualityIssueUpdateFilter
    queryset = QualityIssueUpdate.objects.all()

    def get_queryset(self):
        if 'quality_issue_pk' in self.kwargs:
            get_object_or_404(queryset=QualityIssue.objects.all(),
                              pk=self.kwargs['quality_issue_pk'])

            return super().get_queryset().filter(quality_issue__pk=self.kwargs['quality_issue_pk'])

        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['quality_issue'] = kwargs['quality_issue_pk']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update = self.service.create(
            validated_data=serializer.validated_data,
            user=request.user
        )

        return Response(data=self.get_serializer(update).data, status=status.HTTP_201_CREATED)
