from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.floor_plan_area_pin.floor_plan_area_quality_issue_pin_filter import \
    FloorPlanAreaQualityIssuePinFilter
from api.http.filters.quality_issue.quality_issue_filter import QualityIssueFilter
from api.http.serializers.floor_plan_area_pin.floor_plan_area_quality_issue_pin_serializer import \
    FloorPlanAreaQualityIssuePinSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlanAreaPin, QualityIssue, User
from api.permissions import IsSuperuser, IsProjectAdmin, IsCompanyAdmin, IsProjectManager, IsProjectClient, \
    IsProjectConsultant
from api.services.floor_plan_area_pin_entity_service import FloorPlanAreaPinEntityService


class FloorPlanAreaQualityIssuePinViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'list': (IsAuthenticated, (IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient | IsProjectConsultant),),
    }

    service = FloorPlanAreaPinEntityService()
    serializer_class = FloorPlanAreaQualityIssuePinSerializer
    filterset_class = FloorPlanAreaQualityIssuePinFilter
    queryset = FloorPlanAreaPin.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        quality_issue_filter = QualityIssueFilter(data=request.query_params, queryset=QualityIssue.objects.all(), request=request)
        quality_issue_filter.is_valid()
        subquery = quality_issue_filter.filter_queryset(QualityIssue.objects.add_filters_for_floor_plan_area_pin_subquery(kwargs))

        if request.user.is_client:
            subquery = subquery.filter(user__group__in=[User.Group.CLIENT.value, User.Group.CONSULTANT.value])
        elif request.user.is_consultant:
            subquery = subquery.filter(user__company=request.user.company, user__group=User.Group.CONSULTANT.value)

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
        content_type = ContentType.objects.get_for_model(QualityIssue)
        return super().get_queryset().filter(content_type=content_type)
