from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.serializers import AssetHandoverInformationSerializer
from api.http.views.view import BaseViewSet
from api.models import AssetHandoverInformation
from api.permissions import IsSuperuser, IsCompanyAdmin, IsAdmin, IsManager, IsProjectAdmin, IsProjectManager, \
    IsProjectSubcontractor


class AssetHandoverInformationViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'create': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
        'retrieve': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsAdmin | IsManager,),
        'update': (IsAuthenticated, IsSuperuser | IsCompanyAdmin | IsProjectAdmin | IsProjectManager | IsProjectSubcontractor,),
    }

    serializer_class = AssetHandoverInformationSerializer
    queryset = AssetHandoverInformation.objects.all()
