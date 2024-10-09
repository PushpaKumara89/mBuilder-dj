from django.contrib.contenttypes.models import ContentType
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.floor_plan_revisions.floor_plan_revision_filter import FloorPlanRevisionFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.floor_plan.revisions.floor_plan_revision_serializer import FloorPlanRevisionSerializer
from api.http.views.view import BaseViewSet
from api.models import FloorPlan
from api.models.floor_plan_revision import FloorPlanRevision
from api.permissions import IsCompanyAdmin, IsProjectManager, IsProjectAdmin, IsSuperuser
from api.services.floor_plan_revision_entity_service import FloorPlanRevisionEntityService


class FloorPlanRevisionViewSet(BaseViewSet, ListModelMixin, mixins.RetrieveModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectManager | IsProjectAdmin),
        'retrieve': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectManager | IsProjectAdmin),
        'revert': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectManager | IsProjectAdmin),
    }

    filterset_class = FloorPlanRevisionFilter
    serializer_class = FloorPlanRevisionSerializer
    queryset = FloorPlanRevision.objects.all()
    service = FloorPlanRevisionEntityService()

    def revert(self, request, *args, **kwargs):
        new_revision = self.service.revert_revision(kwargs['floor_plan_pk'], kwargs['pk'], request.user)
        response_data = self.serializer_class(
            new_revision,
            expand=self.serializer_class.Meta.expandable_fields.keys()
        ).data

        return Response(response_data, status=status.HTTP_200_OK)

    def get_queryset(self):
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        return super().get_queryset().filter(version__content_type=floor_plan_content_type).distinct()
