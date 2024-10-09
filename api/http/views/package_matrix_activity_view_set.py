from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.package_matrix_activity_filter import PackageMatrixActivityFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import PackageActivitySerializer
from api.http.views.view import BaseViewSet
from api.models import PackageActivity, Project
from api.permissions import IsStaff, IsProjectClient, IsSuperuser, IsProjectConsultant, IsProjectSubcontractor
from api.permissions.permission_group import PermissionGroup


class PackageMatrixActivityViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsStaff | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
    }

    serializer_class = PackageActivitySerializer
    queryset = PackageActivity.objects.all()
    filterset_class = PackageMatrixActivityFilter
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(packagematrix__project__pk=self.kwargs['project_pk']).distinct()
