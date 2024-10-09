from django_filters import rest_framework
from rest_framework import mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.mixins import ListModelMixin
from api.http.serializers.package_matrix.package_matrix_create_serializer import PackageMatrixCreateSerializer
from api.http.serializers.package_matrix.package_matrix_serializer import PackageMatrixSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, PackageMatrix, LocationMatrixPackage
from api.permissions import IsSuperuser, InProjectEditMode, IsProjectSubcontractor, IsProjectStaff, IsCompanyAdmin, IsAdmin, IsManager
from api.permissions.package_matrix import CanDelete, InEditMode
from api.permissions.permission_group import PermissionGroup
from api.queues.package_handover import cascade_delete_package_handover
from api.queues.core.asset_handover import cascade_delete_asset_handover
from api.queues.hard_delete_tasks import hard_delete_tasks
from api.queues.task import delete_tasks
from api.services.package_matrix_entity_service import PackageMatrixEntityService
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter


class PackageMatrixViewSet(BaseViewSet, ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    _request_permissions = {
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectSubcontractor),),
        'create': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'destroy': (IsAuthenticated, InEditMode, IsSuperuser | CanDelete,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = PackageMatrixSerializer
    queryset = PackageMatrix.objects.all()

    def destroy(self, request, *args, **kwargs):
        package_matrix = self.get_object()
        response = super().destroy(request, *args, **kwargs)

        hard_delete_tasks(
            {'package_activity__packagematrix': kwargs['pk'], 'project_id': package_matrix.project_id},
        )
        delete_tasks(
            {'package_activity__packagematrix': kwargs['pk'], 'project_id': package_matrix.project_id},
        )
        cascade_delete_package_handover([kwargs['pk']])

        LocationMatrixPackage.objects.filter(package_matrix=kwargs['pk']).delete()

        cascade_delete_asset_handover(list(
            LocationMatrixPackage.deleted_objects.filter(package_matrix=kwargs['pk']).values_list('id', flat=True)
        ))

        return response

    def list(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])
        queryset = self.get_queryset().filter(project=project)

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        request_expandable_fields = clean_query_param(
            get_array_parameter('expand', request.query_params),
            rest_framework.CharFilter
        )
        expandable_fields = (['expanded_package_activity.expanded_modified', 'expanded_package', 'expanded_project']
                             + request_expandable_fields)
        serializer = PackageMatrixSerializer(
            queryset,
            many=True,
            expand=set(expandable_fields),
            omit=['package_activity.package_activity_tasks'],
            project_id=project.pk,
            context={'request': self.request, 'view': self}
        )

        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])

        matrix_creation_serializer = PackageMatrixCreateSerializer(data=request.data)
        matrix_creation_serializer.is_valid(raise_exception=True)
        matrix_creation_data = matrix_creation_serializer.validated_data

        package_matrices = self.__prepare_matrix_data(
            matrix_creation_data,
            project.pk,
            matrix_creation_data['package'].pk
        )

        matrix_serializer = PackageMatrixSerializer(data=package_matrices, context={'request': self.request}, many=True)
        matrix_serializer.is_valid(raise_exception=True)
        matrix_serializer.create(matrix_serializer.data)

        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        self.queryset = self.queryset\
            .select_related('project__image', 'package', 'package_activity') \
            .prefetch_related('package_activity__packageactivitytask_set', 'package_activity__files')

        return self.queryset

    def __prepare_matrix_data(self, matrix_creation_data, project_pk, package_pk):
        package_matrices = []
        for package_activity in matrix_creation_data['package_activity']:
            package_matrices.append({
                'project': project_pk,
                'package_activity': package_activity.pk,
                'package': package_pk
            })

        return package_matrices

    def generate_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])
        PackageMatrixEntityService().generate_csv(request, project.id)

        return Response(status=status.HTTP_200_OK)
