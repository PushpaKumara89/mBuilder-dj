from django_filters import rest_framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.package_activity.package_activity_custom_filter import PackageActivityCustomFilter
from api.http.filters.package_activity.package_activity_filter import PackageActivityFilter
from api.http.serializers import PackageActivitySerializer
from api.http.views.view import BaseViewSet
from api.models import PackageActivity, Project
from api.models.queryset import SafeDeleteQueryset
from api.permissions import IsProjectStaff, IsProjectConsultant, IsProjectSubcontractor, IsSuperuser, IsProjectClient, IsStaff, IsCompanyAdmin
from api.permissions.permission_group import PermissionGroup
from api.services.package_activity_entity_service import PackageActivityEntityService
from api.utilities.query_params_utilities import clean_query_param


class PackageActivityViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsStaff | IsProjectSubcontractor | IsProjectClient | IsProjectConsultant),),
        'list_for_handover_documents': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'update': (IsAuthenticated, IsSuperuser,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin,),
        'get_for_matrix': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
    }

    serializer_class = PackageActivitySerializer
    queryset = PackageActivity.objects.prefetch_related('packageactivitytask_set', 'files').all()
    filterset_class = PackageActivityFilter
    search_fields = ['name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = PackageActivityEntityService().create(serializer.validated_data)
        data = self.get_serializer(instance, expand=['expanded_description', 'expanded_description_image']).data
        return Response(data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, expand=['expanded_description', 'expanded_description_image'])
        serializer.is_valid(raise_exception=True)
        PackageActivityEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_for_matrix(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))
        package_activity = get_object_or_404(queryset=PackageActivity.objects.all(), pk=kwargs.get('package_activity_pk'))

        activity = PackageActivity.objects.filter(pk=package_activity.pk, package__projects=project).distinct().get()
        serializer = self.get_serializer(activity, project_id=project.pk)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self._get_response(queryset)

    def list_for_handover_documents(self, request, *args, **kwargs):
        custom_filter = PackageActivityCustomFilter(request)
        custom_filter.add_handover_document()
        queryset = self.filter_queryset(self.queryset.filter(*custom_filter._filter_args, **custom_filter.filter_kwargs).distinct())
        return self._get_response(queryset)

    def get_queryset(self):
        custom_filter = PackageActivityCustomFilter(self.request)
        custom_filter.add_base_queryset_filter()

        return (self.queryset
                .select_related(*custom_filter.select_related)
                .prefetch_related(*custom_filter.prefetch_related)
                .filter(*custom_filter.filter_args, **custom_filter.filter_kwargs)
                .distinct())

    def _get_response(self, queryset: SafeDeleteQueryset) -> Response:
        if self.request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)
        project_id = clean_query_param(
            self.request.query_params.get('project'),
            rest_framework.NumberFilter,
            int
        )

        if page is not None:
            serializer = self.get_serializer(page, many=True, project_id=project_id)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, project_id=project_id)
        return Response(serializer.data)

    def generate_csv(self, request, *args, **kwargs):
        PackageActivityEntityService().generate_csv(request)

        return Response(status=status.HTTP_200_OK)
