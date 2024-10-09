from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView

from api.http.filters.package_matrix_company_filter import PackageMatrixCompanyFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import PackageMatrixCompanySerializer
from api.http.views.view import BaseViewSet
from api.models import PackageMatrixCompany, Project
from api.permissions import IsSuperuser, InProjectEditMode
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup


class PackageMatrixCompanyViewSet(ListBulkCreateUpdateDestroyAPIView, BaseViewSet,
                                  ListModelMixin, mixins.DestroyModelMixin):
    _request_permissions = {
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'create': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'destroy': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
    }

    serializer_class = PackageMatrixCompanySerializer
    queryset = PackageMatrixCompany.objects.all()
    filterset_class = PackageMatrixCompanyFilter

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            project = get_object_or_404(queryset=Project.objects.all(), pk=self.kwargs['project_pk'])
            self.queryset = self.queryset.filter(package_matrix__project=project)

        return self.queryset
