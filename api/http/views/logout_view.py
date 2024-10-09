from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.http.serializers import LogoutSerializer
from api.models import EditMode
from api.services.user_entity_service import UserEntityService


class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserEntityService().logout(serializer.token)

        force_remove_edit_mode = request.data.get('force_remove_edit_mode')
        if type(force_remove_edit_mode) == bool and force_remove_edit_mode:
            EditMode.objects.filter(user=request.user.pk).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)