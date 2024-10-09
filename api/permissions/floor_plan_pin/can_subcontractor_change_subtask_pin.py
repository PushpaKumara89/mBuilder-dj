from rest_framework.permissions import BasePermission

from api.models import Subtask


class CanSubcontractorChangeSubtaskPin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_subcontractor and \
               Subtask.objects.filter(pk=view.kwargs['subtask_pk'], company=request.user.company).exists()
