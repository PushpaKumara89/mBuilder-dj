from rest_framework.permissions import BasePermission

from api.models import Project, PackageHandover


class DoesProjectSubcontractorCanUpdate(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return user.is_subcontractor and \
            Project.objects.filter(pk=view.kwargs['project_pk'], users=user).exists() and \
            PackageHandover.objects.filter(pk=view.kwargs['pk'],
                                           package_matrix__packagematrixcompany__company_id=user.company_id).exists()
