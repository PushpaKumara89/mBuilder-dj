from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.project_filter import ProjectFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.project_key_contacts_serializer import ProjectKeyContactsSerializer
from api.http.serializers.project_serializer import ProjectSerializer
from api.http.serializers.project_user_serializer import ProjectUserSerializer
from api.http.serializers.project_users_serializer import ProjectUsersSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, ProjectUser
from api.permissions import IsSuperuser, IsConsultant, IsSubcontractor, IsCompanyAdmin, IsAdmin, IsManager
from api.permissions.permission_group import PermissionGroup
from api.permissions.projects import IsProjectStaff, RemovesHimself, IsProjectClient, DoesProjectHasUsersFromSameCompany
from api.services.project_entity_service import ProjectEntityService
from api.utilities.helpers import is_expanded


class ProjectViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | PermissionGroup(PermissionGroup(IsConsultant | IsSubcontractor) & DoesProjectHasUsersFromSameCompany, ), ),),
        'list': (HasAPIKey | IsAuthenticated,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'update': (IsAuthenticated, IsSuperuser | IsProjectStaff),
        'update_user': (IsAuthenticated, IsSuperuser,),
        'add_users': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'remove_users': (IsAuthenticated, IsSuperuser | RemovesHimself | (IsAdmin & IsProjectStaff),),
        'add_key_contacts': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'remove_key_contacts': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = ProjectSerializer
    queryset = Project.objects.select_related('image').all()
    filterset_class = ProjectFilter
    search_fields = ['name', 'number']

    def get_queryset(self):
        if is_expanded(self.request, 'expanded_news'):
            self.queryset = self.queryset.prefetch_related('projectnews_set')

        if is_expanded(self.request, 'expanded_key_contacts'):
            self.queryset = self.queryset.prefetch_related('key_contacts')

        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = ProjectEntityService().create_project(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = ProjectEntityService().update_project(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(self.get_serializer(instance).data)

    def update_user(self, request, *args, **kwargs):
        project_user = get_object_or_404(ProjectUser.objects.all(), project_id=kwargs['project_pk'], user_id=kwargs['user_pk'])

        serializer = ProjectUserSerializer(project_user, data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectEntityService().update(project_user, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True

        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter_by_user_permissions(request.user)

        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        ProjectEntityService().destroy_project(kwargs['pk'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], url_path='users/add')
    def add_users(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectUsersSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectEntityService().add_users(instance, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='key-contacts/add')
    def add_key_contacts(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectKeyContactsSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectEntityService().add_key_contacts(instance, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='users/remove')
    def remove_users(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectUsersSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectEntityService().remove_users(instance, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='key-contacts/remove')
    def remove_key_contacts(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectKeyContactsSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        ProjectEntityService().remove_key_contacts(instance, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    def generate_csv(self, request, *args, **kwargs):
        ProjectEntityService().generate_csv(request)

        return Response(status=status.HTTP_200_OK)
