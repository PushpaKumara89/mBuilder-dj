from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.floor_plan_building_filter import FloorPlanBuildingFilter
from api.http.mixins import ListModelMixin
from api.http.views.view import BaseViewSet
from api.models import FloorPlan
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager


class FloorPlanBuildingViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    queryset = FloorPlan.objects.all()
    filterset_class = FloorPlanBuildingFilter

    def get_queryset(self) -> QuerySet:
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(project=self.kwargs['project_pk'])
        return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).values('building').distinct('building').order_by('building')

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(data=list(queryset))
