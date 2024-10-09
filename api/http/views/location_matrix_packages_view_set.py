from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.location_matrix_package_filter import LocationMatrixPackageFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.location_matrix_package import LocationMatrixPackagesSerializer, LocationMatrixPackagesMediaSerializer
from api.http.views.view import BaseViewSet
from api.models import LocationMatrixPackage, Project
from api.permissions import IsSuperuser, InProjectEditMode, IsProjectStaff, IsCompanyAdmin, IsAdmin, IsManager
from api.permissions.permission_group import PermissionGroup
from api.services.location_matrix_package_entity_service import LocationMatrixPackageEntityService


class LocationMatrixPackagesViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'destroy': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'create': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'partial_update': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'update': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'sync': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'add_media': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'remove_media': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = LocationMatrixPackagesSerializer
    queryset = LocationMatrixPackage.objects.all()
    filterset_class = LocationMatrixPackageFilter

    def list(self, request, *args, **kwargs):
        queryset = (self.filter_queryset(self.queryset.filter(location_matrix__project=kwargs['project_pk']))
                        .annotate(media_count=Count('media')))

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                expand=['expanded_media_count'],
            )

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
            expand=['expanded_media_count'],
        )

        return Response(serializer.data)

    def sync(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True, partial=True)
        serializer.sync(request.user)

        if not serializer.updated_entities:
            return Response(data={})

        queryset = self.filter_queryset(serializer.updated_entities).annotate(media_count=Count('media'))

        serializer = self.get_serializer(
            queryset,
            many=True,
            expand=['expanded_media_count'],
        )

        return Response(data=serializer.data)

    def add_media(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = LocationMatrixPackagesMediaSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add()

        return Response(status=status.HTTP_200_OK)

    def remove_media(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = LocationMatrixPackagesMediaSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.remove()

        return Response(status=status.HTTP_200_OK)

    def generate_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['project_pk'])
        LocationMatrixPackageEntityService().generate_csv(request, project.id)

        return Response(status=status.HTTP_200_OK)
