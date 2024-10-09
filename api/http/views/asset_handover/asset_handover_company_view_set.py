from django.db.models import Q, F, BooleanField
from django.db.models.expressions import Case, RawSQL, When
from rest_framework.permissions import IsAuthenticated

from api.http.filters.asset_handover.asset_handover_company_filter import AssetHandoverCompanyFilterKwargs
from api.http.mixins import ListModelMixin
from api.http.serializers import CompanySerializer
from api.http.views.view import BaseViewSet
from api.models import Company
from api.permissions import IsCompanyAdmin, IsProjectAdmin, IsProjectManager, IsProjectClient
from api.utilities.helpers import is_expanded


class AssetHandoverCompanyViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient,)
    }

    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    filterset_class = AssetHandoverCompanyFilterKwargs

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_kwargs = {
            'assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__project_id': self.kwargs['project_pk'],
            'assethandoverdocumentmediaupdate__deleted__isnull': True,
            'assethandoverdocumentmediaupdate__asset_handover_document_media__deleted__isnull': True,
            'assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__deleted__isnull': True,
            'assethandoverdocumentmediaupdate__asset_handover_document_media__asset_handover_document__asset_handover__deleted__isnull': True,
        }

        filter_ = AssetHandoverCompanyFilterKwargs(self.request.GET, queryset=queryset)
        filter_kwargs.update(**filter_.get_filter_kwargs())

        filter_args = [
            Q(assethandoverdocumentmediaupdate__old_data={})
            | Q(
                same_media=False,
                assethandoverdocumentmediaupdate__old_data__media__isnull=False
            )
        ]

        self.queryset = queryset.annotate(
            same_media=Case(
                When(RawSQL('old_data -> %s = new_data -> %s', ('media', 'media'), output_field=BooleanField()), then=True),
                default=False,
                output_field=BooleanField()
            )
        ).filter(*filter_args, **filter_kwargs).distinct()

        if is_expanded(self.request, 'expanded_users_count'):
            self.queryset = self.queryset.prefetch_related('user_set')

        return self.queryset
