from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.http.serializers.app_settings_serializer import AppSettingsSerializer
from api.http.serializers.settings_registration_user_serializer import SettingsRegistrationUserSerializer
from api.http.views import BaseViewSet
from api.permissions import IsSuperuser
from api.services.settings_registration_user_service import AppSettingsService
from api.utilities.swagger_helpers import errors_response_scheme


class AppSettingsViewSet(BaseViewSet):
    _request_permissions = {
        'retrieve': [IsAuthenticated, IsSuperuser],
        'update': [IsAuthenticated, IsSuperuser],
        'check_pre_register_settings': [AllowAny],
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: AppSettingsSerializer,
                                    status.HTTP_400_BAD_REQUEST: errors_response_scheme('Bad request'),
                                    status.HTTP_403_FORBIDDEN: errors_response_scheme('Forbidden'),
                                    status.HTTP_500_INTERNAL_SERVER_ERROR: errors_response_scheme('Internal Server Error')},
                         request_body=AppSettingsSerializer,
                         operation_id='update_app_settings')
    def update(self, request):
        instance = AppSettingsService.get_or_create()
        serializer = AppSettingsSerializer(instance, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = AppSettingsService(instance).update(serializer.validated_data)
        return Response(AppSettingsSerializer(instance, context={'request': request}).data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: AppSettingsSerializer,
                                    status.HTTP_400_BAD_REQUEST: errors_response_scheme('Bad request'),
                                    status.HTTP_403_FORBIDDEN: errors_response_scheme('Forbidden'),
                                    status.HTTP_500_INTERNAL_SERVER_ERROR: errors_response_scheme('Internal Server Error')},
                         operation_id='retrieve_app_settings')
    def retrieve(self, request):
        instance = AppSettingsService.get_or_create()
        return Response(AppSettingsSerializer(instance, context={'request': request}).data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: SettingsRegistrationUserSerializer,
                                    status.HTTP_500_INTERNAL_SERVER_ERROR: errors_response_scheme('Internal Server Error')},
                         methods=['GET'],
                         operation_id='check_pre_register_settings')
    @action(methods=['GET'], detail=False, url_path=r'check-pre-register-settings', url_name='check_pre_register_settings', filter_backends=[], pagination_class=None)
    def check_pre_register_settings(self, request):
        instance = AppSettingsService.get_or_create()
        return Response(SettingsRegistrationUserSerializer(instance, context={'request': request}).data)
