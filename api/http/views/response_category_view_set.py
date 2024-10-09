from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.filters.response_category_filter import ResponseCategoryFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import ResponseCategorySerializer
from api.http.views.view import BaseViewSet
from api.models import ResponseCategory, Project
from api.permissions import IsSuperuser, IsProjectUser
from api.permissions.is_company_admin import IsCompanyAdmin
from api.services.response_category_entity_service import ResponseCategoryEntityService


class ResponseCategoryViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsCompanyAdmin | IsSuperuser,),
        'create': (IsAuthenticated, IsCompanyAdmin | IsSuperuser,),
        'retrieve': (IsAuthenticated, IsCompanyAdmin | IsSuperuser | IsProjectUser,),
        'list': (IsAuthenticated, IsCompanyAdmin | IsSuperuser | IsProjectUser,),
        'destroy': (IsAuthenticated, IsCompanyAdmin | IsSuperuser,),
    }

    serializer_class = ResponseCategorySerializer
    filterset_class = ResponseCategoryFilter
    queryset = ResponseCategory.objects.all()
    search_fields = ['name', 'description']

    def get_queryset(self):
        return self.queryset.filter(project=self.kwargs['project_pk'])

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))
        request.data['project'] = project.pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ResponseCategoryEntityService().create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        ResponseCategoryEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
