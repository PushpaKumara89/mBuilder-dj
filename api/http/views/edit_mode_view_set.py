from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.edit_mode_filter import EditModeFilter
from api.http.serializers.edit_mode_serializer import EditModeSerializer
from api.http.views.view import BaseViewSet
from api.models.edit_mode import EditMode
from api.permissions import IsSuperuser, IsProjectClient, IsProjectConsultant
from api.permissions.edit_mode import CanManage
from api.permissions import IsProjectStaff


class EditModeViewSet(BaseViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    _request_permissions = {
        'destroy': (IsAuthenticated, CanManage,),
        'create': (IsAuthenticated, CanManage,),
        'retrieve': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectClient | IsProjectConsultant),
    }

    serializer_class = EditModeSerializer
    queryset = EditMode.objects.all()
    filterset_class = EditModeFilter

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        request.data['project'] = kwargs['project_pk']

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset.filter(user=request.user.pk, project=kwargs['project_pk']).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.queryset.filter(project=kwargs['project_pk']).first()
        if queryset is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset)

        return Response(serializer.data)
