from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.floor_plan_level_filter import FloorPlanLevelFilter
from api.http.mixins import ListModelMixin
from api.http.views.view import BaseViewSet
from api.models import FloorPlan
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager


class FloorPlanLevelViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager),),
    }

    queryset = FloorPlan.objects.all()
    filterset_class = FloorPlanLevelFilter

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(project=self.kwargs['project_pk'])
        return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).values('level').distinct('level').order_by('level')

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(data=list(queryset))
