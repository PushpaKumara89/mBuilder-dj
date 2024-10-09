from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.floor_plan_area_pin.floor_plan_area_subtask_pin_filter import FloorPlanAreaSubtaskPinFilter
from api.http.filters.subtask import SubtaskFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.floor_plan_area_pin.floor_plan_area_subtask_pin_serializer import FloorPlanAreaSubtaskPinSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlanAreaPin, Subtask
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager, IsProjectSubcontractor
from api.permissions.subtasks.can_client_see_project_subtasks import CanClientSeeProjectSubtasks
from api.services.floor_plan_area_pin_entity_service import FloorPlanAreaPinEntityService


class FloorPlanAreaSubtaskPinViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | CanClientSeeProjectSubtasks | IsProjectSubcontractor),),
    }

    service = FloorPlanAreaPinEntityService()
    serializer_class = FloorPlanAreaSubtaskPinSerializer
    filterset_class = FloorPlanAreaSubtaskPinFilter
    queryset = FloorPlanAreaPin.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        subtask_filter = SubtaskFilter(data=request.query_params, queryset=Subtask.objects.all(), request=request)
        subtask_filter.is_valid()
        subquery = subtask_filter.filter_queryset(Subtask.objects.add_filters_for_floor_plan_area_pin_subquery(kwargs))

        if self.request.user.is_subcontractor:
            subquery = subquery.filter(company=self.request.user.company)

        if self.request.user.is_client:
            subquery = subquery.filter(quality_issue__isnull=True)

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

    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(Subtask)
        return super().get_queryset().filter(content_type=content_type)
