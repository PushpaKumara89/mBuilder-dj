from django.db.models import Sum

from api.models.managers import BaseManager


class PackageHandoverStatisticsManager(BaseManager):
    def aggregate_status_counter_for_project(self, project_pk: int, user=None):
        filters = {
            'project__pk': project_pk,
            'group__isnull': True,
            'company__isnull': True,
        }

        if user is not None and (user.is_subcontractor or user.is_consultant):
            filters['company_id'] = user.company_id
            filters['group__isnull'] = False
            del filters['company__isnull']

        return (self.get_queryset()
                .filter(**filters)
                .aggregate(in_progress_count=Sum('in_progress_count'),
                           removed_count=Sum('removed_count'),
                           contested_count=Sum('contested_count'),
                           accepted_count=Sum('accepted_count'),
                           requesting_approval_count=Sum('requesting_approval_count'),
                           requested_approval_rejected_count=Sum('requested_approval_rejected_count')))
