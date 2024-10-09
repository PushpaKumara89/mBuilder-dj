import json

from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class ResetPasswordAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_user = request.user

        if request.path == '/api/password-reset/confirm/':
            request_data = json.loads(request.body)
            reset_password_token = ResetPasswordToken.objects.filter(key=request_data['token']).first()

            if reset_password_token is not None:
                request_user = reset_password_token.user

        response = self.get_response(request)

        if request.path == '/api/password-reset/confirm/' and response.status_code == status.HTTP_200_OK:
            tokens = self.__get_tokens_for_user(request_user)

            response.data = {**response.data, **tokens}
            response.content = json.dumps(response.data)

        return response

    def __get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
