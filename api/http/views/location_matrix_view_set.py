import os

from django.http import StreamingHttpResponse
from django_filters import rest_framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters import LocationMatrixFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import LocationMatrixSerializer
from api.http.serializers.location_matrix.location_matrix_qr_codes_serializer import LocationMatrixQRCodesSerializer
from api.http.views.view import BaseViewSet
from api.models import LocationMatrix, Project
from api.permissions import IsSuperuser, InProjectEditMode, IsProjectConsultant, IsProjectSubcontractor, IsCompanyAdmin, IsAdmin, IsManager
from api.permissions.location_matrix import IsLocationMatrixProjectStaff, InEditMode
from api.permissions import IsProjectClient
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup
from api.services.location_matrix_entity_service import LocationMatrixEntityService
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter
from api.utilities.location_matrix_utilities import annotate_location_matrix_level_parts


class LocationMatrixViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, InEditMode, IsSuperuser | IsLocationMatrixProjectStaff,),
        'partial_update': (IsAuthenticated, InEditMode, IsSuperuser | IsLocationMatrixProjectStaff,),
        'create': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsLocationMatrixProjectStaff),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant | IsProjectSubcontractor),),
        'destroy': (IsAuthenticated, InEditMode, IsSuperuser | IsLocationMatrixProjectStaff,),
        'sync': (IsAuthenticated, InProjectEditMode, IsSuperuser | IsProjectStaff,),
        'qr_codes': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = LocationMatrixSerializer
    queryset = LocationMatrix.objects.all()
    filterset_class = LocationMatrixFilter

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['project_pk'])
        request.data['project'] = project.pk

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = self.__get_ordered_queryset(kwargs['project_pk'])

        return super().list(request, *args, **kwargs)

    def sync(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])
        for location in request.data:
            location['project'] = project.pk

        serializer = self.get_serializer(data=request.data, many=True, parent_id=project.pk, context={'request': self.request})
        serializer.sync()

        queryset = self.__get_ordered_queryset(project.pk)
        response = self.get_serializer(queryset, many=True)

        return Response(data=response.data, status=status.HTTP_200_OK)

    def qr_codes(self, request, *args, **kwargs):
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

        buildings = clean_query_param(
            get_array_parameter('building', request.query_params),
            rest_framework
        )

        levels = clean_query_param(
            get_array_parameter('level', request.query_params),
            rest_framework
        )

        areas = clean_query_param(
            get_array_parameter('area', request.query_params),
            rest_framework
        )

        serializer = LocationMatrixQRCodesSerializer(data={
            'project': kwargs['project_pk'],
            'building': buildings,
            'level': levels,
            'area': areas
        })
        serializer.is_valid(raise_exception=True)
        buffer = serializer.generate()

        response = StreamingHttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s_QR-codes.pdf"' % serializer.validated_data['project'].name_without_spaces

        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'false'

        return response

    def __get_ordered_queryset(self, project_pk):
        queryset = annotate_location_matrix_level_parts(LocationMatrix.objects)

        return self.filter_queryset(
            queryset.filter(project=project_pk).order_by('building', '-level_number', 'level_postfix', 'area').all()
        ).distinct()

    def generate_csv(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.all(), pk=kwargs['project_pk'])
        LocationMatrixEntityService().generate_csv(request, project.id)

        return Response(status=status.HTTP_200_OK)
