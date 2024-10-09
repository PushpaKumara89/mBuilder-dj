from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters.floor_plan_package_filter import FloorPlanPackageFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.floor_plan.floor_plan_package_serializer import FloorPlanPackageSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlan
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager


class FloorPlanPackageViewSet(BaseViewSet, ModelViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    queryset = FloorPlan.objects.all()
    filterset_class = FloorPlanPackageFilter
    serializer_class = FloorPlanPackageSerializer

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(project=self.kwargs['project_pk'])
        return self.queryset
