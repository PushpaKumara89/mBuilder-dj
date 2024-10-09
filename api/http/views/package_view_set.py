from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.package_filter import PackageFilter, PackageCustomPackageMatrixFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.packages.package_serializer import PackageSerializer
from api.http.views.view import BaseViewSet
from api.models import Package, LocationMatrixPackage
from api.permissions import IsSuperuser, IsStaff, IsProjectClient, IsProjectStaff, IsProjectConsultant, IsProjectSubcontractor, IsCompanyAdmin
from api.permissions.permission_group import PermissionGroup
from api.services.package_entity_service import PackageEntityService
from api.utilities.helpers import is_expanded


class PackageViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsStaff, ),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'update': (IsAuthenticated, IsSuperuser,),
        'sync': (IsAuthenticated, IsSuperuser,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin,),
        'matrix_packages': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
    }

    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    filterset_class = PackageFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PackageEntityService().create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        PackageEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def sync(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=(request.data or []), many=True)

        with transaction.atomic():
            PackageEntityService().sync_delete_nonexistent(serializer.initial_data)
            serializer.is_valid(raise_exception=True)
            PackageEntityService().sync(serializer.validated_data, serializer.initial_data)

        queryset = self.filter_queryset(Package.objects.values())
        response = self.get_serializer(queryset, many=True)

        return Response(data=response.data)

    def matrix_packages(self, request, *args, **kwargs):
        custom_filter = PackageCustomPackageMatrixFilter(self.request, self.kwargs.get('project_pk'))
        custom_filter.add_location_filters()
        custom_filter.add_package_handover_filters()
        custom_filter.add_asset_handover_filters()
        custom_filter.add_tasks_filters()
        custom_filter.add_handover_document_filters()
        custom_filter.add_filter_by_company()

        self.queryset = Package.objects.distinct().filter(*custom_filter.filter_args, **custom_filter.filter_kwargs).order_by('order')

        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        if is_expanded(self.request, 'expanded_projects_count'):
            self.queryset = self.queryset.get_expanded_projects_count()
        return self.queryset

    def generate_csv(self, request, *args, **kwargs):
        PackageEntityService().generate_csv(request)

        return Response(status=status.HTTP_200_OK)
