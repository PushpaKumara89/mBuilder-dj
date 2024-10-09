from django.db.models import Q, BooleanField
from django.db.models.expressions import Case, When, RawSQL
from rest_framework.permissions import IsAuthenticated

from api.http.filters.package_handover_company_filter import PackageHandoverCompanyFilterKwargs
from api.http.mixins import ListModelMixin
from api.http.serializers import CompanySerializer
from api.http.views.view import BaseViewSet
from api.models import Company
from api.permissions import IsCompanyAdmin, IsProjectAdmin, IsProjectManager, IsProjectClient
from api.utilities.helpers import is_expanded


class PackageHandoverCompanyViewSet(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectClient,)
    }

    serializer_class = CompanySerializer
    queryset = Company.objects.filter()
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_kwargs = {
            'packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__project_id': self.kwargs['project_pk'],
            'packagehandoverdocumentmediaupdate__package_handover_document_media__package_handover_document__deleted__isnull': True,
            'packagehandoverdocumentmediaupdate__package_handover_document_media__deleted__isnull': True,
            'packagehandoverdocumentmediaupdate__deleted__isnull': True,
        }

        filter_ = PackageHandoverCompanyFilterKwargs(self.request.GET, queryset=queryset)
        filter_kwargs.update(**filter_.get_filter_kwargs())

        filter_args = [
            Q(packagehandoverdocumentmediaupdate__old_data={})
            | Q(
                same_media=False,
                packagehandoverdocumentmediaupdate__old_data__media__isnull=False,
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
