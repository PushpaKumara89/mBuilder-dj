from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.project_news_filter import ProjectNewsFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.project_news_serializer import ProjectNewsSerializer
from api.http.views.view import BaseViewSet
from api.models.project_news import ProjectNews
from api.permissions import IsSuperuser, IsStaff
from api.permissions.permission_group import PermissionGroup
from api.permissions.project_news import CanCreate, CanRetrieve, CanManage
from api.services.project_news_entity_service import ProjectNewsEntityService


class ProjectNewsViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | CanRetrieve, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsStaff, ),),
        'destroy': (IsAuthenticated, IsSuperuser | CanManage,),
        'create': (IsAuthenticated, IsSuperuser | CanCreate,),
        'update': (IsAuthenticated, IsSuperuser | CanManage,),
    }

    serializer_class = ProjectNewsSerializer
    queryset = ProjectNews.objects.all()
    filterset_class = ProjectNewsFilter
    search_fields = ['title', 'text']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectNewsEntityService().create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        ProjectNewsEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
