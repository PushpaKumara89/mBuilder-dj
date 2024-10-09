from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.http.serializers.asset_register_serializer import AssetRegisterSerializer
from api.http.views.view import BaseViewSet
from api.models import Project, AssetRegister
from api.permissions import IsSuperuser, IsProjectCompanyAdmin, IsProjectUser
from api.services.asset_register_entity_service import AssetRegisterEntityService


class AssetRegisterViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, (IsSuperuser | IsProjectCompanyAdmin),),
        'create': (IsAuthenticated, (IsSuperuser | IsProjectCompanyAdmin),),
        'retrieve': (IsAuthenticated, (IsSuperuser | IsProjectUser),),
        'destroy': (IsAuthenticated, (IsSuperuser | IsProjectCompanyAdmin),),
    }

    serializer_class = AssetRegisterSerializer
    queryset = AssetRegister.objects.all()
    service = AssetRegisterEntityService()

    def get_queryset(self):
        if 'project_pk' in self.kwargs:
            self.queryset = self.queryset.filter(project=self.kwargs['project_pk'])

        return self.queryset

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))
        request.data['project'] = project.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_asset_register = self.service.create(serializer.validated_data)
        response_data = self.serializer_class(created_asset_register).data

        return Response(data=response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(queryset=AssetRegister.objects.all(), project=kwargs.get('project_pk'))
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs.get('project_pk'))
        request.data['project'] = project.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_asset_register = self.service.update(instance, serializer.validated_data)
        response_data = self.serializer_class(updated_asset_register).data

        return Response(data=response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(queryset=AssetRegister.objects.all(), project=kwargs.get('project_pk'))

        return Response(data=self.get_serializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(queryset=AssetRegister.objects.all(), project=kwargs.get('project_pk'))
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
