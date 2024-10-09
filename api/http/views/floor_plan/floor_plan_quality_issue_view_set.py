from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef
from django_filters import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.floor_plan.floor_plan_filter import FloorPlanFilter
from api.http.filters.quality_issue.quality_issue_filter import QualityIssueFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import FloorPlanSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlan, QualityIssue, FloorPlanArea
from api.permissions import IsSuperuser, IsCompanyAdmin, IsProjectManager, IsProjectAdmin, IsProjectClient, \
    IsProjectConsultant
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter


class FloorPlanQualityIssueViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | IsProjectConsultant),),
    }

    serializer_class = FloorPlanSerializer
    queryset = FloorPlan.objects.all()
    filterset_class = FloorPlanFilter

    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(QualityIssue)
        area_filter = clean_query_param(
            get_array_parameter('area', self.request.query_params),
            rest_framework.CharFilter
        )
        floor_plan_area_filters = {
            'floorplanareapin__content_type': content_type,
            'floorplanareapin__deleted__isnull': True,
            'deleted__isnull': True,
        }
        filters = {}

        if area_filter:
            floor_plan_area_filters['area__in'] = area_filter

        if 'project_pk' in self.kwargs:
            filters['project'] = self.kwargs['project_pk']

        return self.queryset.filter(Exists(FloorPlanArea.objects.filter(floor_plan=OuterRef('id'), **floor_plan_area_filters)), **filters)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        quality_issue_filter = QualityIssueFilter(data=request.query_params, queryset=QualityIssue.objects.all(), request=request)
        quality_issue_filter.is_valid()
        subquery = quality_issue_filter.filter_queryset(QualityIssue.objects.add_filters_for_floor_plan_subquery())
        queryset = queryset.filter(Exists(subquery))

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
