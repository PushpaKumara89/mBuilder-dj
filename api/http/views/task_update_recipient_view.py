from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.recipient import TaskUpdateRecipientsFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import RecipientSerializer
from api.http.views.view import BaseViewSet
from api.models import Recipient
from api.permissions import IsSuperuser
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup


class TaskUpdateRecipientView(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
    }

    queryset = Recipient.objects.only_active()
    serializer_class = RecipientSerializer
    filterset_class = TaskUpdateRecipientsFilter

    def list(self, request, *args, **kwargs):
        self.queryset = self.get_queryset() \
            .filter(taskupdate__task__location_matrix__project=kwargs['project_pk']) \
            .distinct('email') \
            .order_by('email')

        return super().list(request, *args, **kwargs)
