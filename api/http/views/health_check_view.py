from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.http.views.view import BaseViewSet


class HealthCheckView(BaseViewSet):
    _request_permissions = {
        'check': (AllowAny,),
    }

    @action(methods=['GET'], detail=False)
    def check(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
