from django.db.models import Exists, OuterRef
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.recipient import SubtaskUpdateRecipientsFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import RecipientSerializer
from api.http.views.view import BaseViewSet
from api.models import Recipient, User
from api.permissions import IsSuperuser, IsProjectSubcontractor
from api.permissions import IsProjectStaff
from api.permissions.permission_group import PermissionGroup


class SubtaskUpdateRecipientView(BaseViewSet, ListModelMixin):
    _request_permissions = {
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectSubcontractor),),
    }

    queryset = Recipient.objects.only_active()
    serializer_class = RecipientSerializer
    filterset_class = SubtaskUpdateRecipientsFilter

    def list(self, request, *args, **kwargs):
        filters = []
        if request.user.is_subcontractor:
            filters.append(
                ~Exists(User.objects.filter(
                    email=OuterRef('email'),
                    groups__in=[User.Group.CLIENT.value, User.Group.CONSULTANT.value],
                    deleted__isnull=True
                ))
            )

        self.queryset = self.get_queryset() \
            .filter(
                *filters,
                subtaskupdate__subtask__task__location_matrix__project_id=kwargs['project_pk'],
                subtaskupdate__subtask__task__location_matrix__deleted__isnull=True,
                subtaskupdate__subtask__task__deleted__isnull=True,
                subtaskupdate__subtask__deleted__isnull=True
            ).distinct('email').order_by('email')

        return super().list(request, *args, **kwargs)
