from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.http.serializers import UserSerializer, LogoutSerializer
from api.http.views.view import BaseViewSet
from api.models import User
from api.permissions import AllowedToAssignCompanyAdminRole
from api.services.user_entity_service import UserEntityService


class ProfileViewSet(BaseViewSet):
    _request_permissions = {
        'profile': (permissions.IsAuthenticated, AllowedToAssignCompanyAdminRole,),
    }

    serializer_class = UserSerializer
    queryset = User.objects.only_active()

    @action(detail=False, methods=['get', 'put', 'delete'])
    def profile(self, request, *args, **kwargs):
        if request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            UserEntityService().update(serializer.instance, serializer.validated_data)

            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'GET':
            serializer = self.get_serializer(request.user)

            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                UserEntityService().logout(serializer.token)
                UserEntityService().delete_own_profile(request.user)

            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'method': self.request.method}
        return super().get_serializer(*args, **kwargs)
