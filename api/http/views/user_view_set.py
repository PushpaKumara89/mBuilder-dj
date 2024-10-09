from django_filters import rest_framework
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.user_filter import UserFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import UserSerializer
from api.http.serializers.user.user_restore_serializer import UserRestoreSerializer
from api.http.views.view import BaseViewSet
from api.models import User
from api.permissions import AllowedToAssignCompanyAdminRole,  IsSuperuser, IsStaff, IsCompanyAdmin, IsAdmin, IsManager
from api.permissions.permission_group import PermissionGroup
from api.permissions.users import AllowedToUpdateCompanyAdmin, IsProjectUser
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions.users.can_change_is_api_access_allowed import CanChangeIsApiAccessAllowed
from api.services.user_entity_service import UserEntityService
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import is_expanded, get_array_parameter


class UserViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser | IsStaff & AllowedToUpdateCompanyAdmin & AllowedToAssignCompanyAdminRole, CanChangeIsApiAccessAllowed),
        'partial_update': (IsAuthenticated, IsSuperuser | IsStaff & AllowedToUpdateCompanyAdmin & AllowedToAssignCompanyAdminRole,),
        'create': (IsAuthenticated, IsSuperuser | IsStaff & AllowedToAssignCompanyAdminRole,),
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsStaff),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsStaff | IsProjectUser),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'restore': (IsAuthenticated, IsSuperuser,),
        'register': (AllowAny,),
        'approve': (IsAuthenticated, IsSuperuser,),
        'delete_own_account': (IsAuthenticated,),
        'generate_csv': (IsAuthenticated, IsCompanyAdmin | IsAdmin | IsManager,),
    }

    serializer_class = UserSerializer
    queryset = User.objects.only_active()
    filterset_class = UserFilter
    search_fields = ['first_name', 'email', 'last_name', 'company__name']

    def get_serializer(self, *args, **kwargs):
        _action = {'action': self.action}
        kwargs['context'] = {**kwargs['context'], **_action} if 'context' in kwargs else _action
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        if is_expanded(self.request, 'expanded_projects'):
            self.queryset = self.queryset.prefetch_related('project_set')

        if is_expanded(self.request, 'expanded_user_company'):
            self.queryset = self.queryset.select_related('company')

        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserEntityService().create(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        UserEntityService().update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if 'project' in request.query_params:
            expand = get_array_parameter('expand', request.query_params)

            if 'expanded_is_notifications_enabled' in expand:
                project = clean_query_param(
                    request.query_params['project'],
                    rest_framework.NumberFilter,
                    int
                )
                self.queryset = self.queryset.add_notifications_enabled(project)

        return super().list(request, *args, **kwargs)

    @action(methods=['POST'], detail=True)
    def restore(self, request, *args, **kwargs):
        serializer = UserRestoreSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        UserEntityService().restore(serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=True)
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        UserEntityService().update(instance, {'status': User.Status.APPROVED})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserEntityService().register(serializer.validated_data)
        UserEntityService().notify_company_admins_registration_user(user.id)

        refresh = RefreshToken.for_user(user)

        return Response(status=status.HTTP_201_CREATED, data={
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    def generate_csv(self, request, *args, **kwargs):
        UserEntityService().generate_csv(request)

        return Response(status=status.HTTP_200_OK)
