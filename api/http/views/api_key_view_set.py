from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.api_key.api_key_filter import ApiKeyFilter
from api.http.mixins import ListModelMixin
from api.http.serializers.api_key.api_key_serializer import ApiKeySerializer
from api.http.views.view import BaseViewSet
from api.models import ApiKey
from api.permissions import IsCompanyAdmin, IsSuperuser
from api.services.api_key_entity_service import ApiKeyEntityService


class ApiKeyViewSet(BaseViewSet, ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    _request_permissions = {
        'list': (IsAuthenticated, IsSuperuser | IsCompanyAdmin),
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin),
        'update': (IsAuthenticated, IsSuperuser | IsCompanyAdmin),
        'destroy': (IsAuthenticated, IsSuperuser | IsCompanyAdmin),
    }

    service = ApiKeyEntityService()
    filterset_class = ApiKeyFilter
    serializer_class = ApiKeySerializer
    queryset = ApiKey.objects.all()
    search_fields = ['project__name', 'project__number', 'token', 'company__name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.create(
            validated_data=serializer.validated_data,
        )

        return Response(data=self.get_serializer(result).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        api_key = self.get_object()
        serializer = self.get_serializer(api_key, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        result = self.service.update(
            instance=api_key,
            validated_data=serializer.validated_data,
        )

        return Response(data=self.get_serializer(result).data)
