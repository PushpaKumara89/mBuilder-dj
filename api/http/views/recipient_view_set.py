from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.recipient.recipient_filter import RecipientFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import RecipientSerializer
from api.http.views.view import BaseViewSet
from api.models import Recipient
from api.permissions import IsSuperuser
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup


class RecipientViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser, ),),
        'create': (IsAuthenticated, IsSuperuser,),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'update': (IsAuthenticated, IsSuperuser,),
    }

    serializer_class = RecipientSerializer
    queryset = Recipient.objects.only_active()
    filterset_class = RecipientFilter
