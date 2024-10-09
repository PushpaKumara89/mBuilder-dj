from django.db.models import Q

from api.models.queryset import SafeDeleteQueryset


class TaskQueryset(SafeDeleteQueryset):
    def exclude_not_applicable(self):
        return self.filter(~Q(status=self.model.Statuses.NOT_APPLICABLE.value))

    def filter_by_project(self, kwargs):
        if 'project_pk' in kwargs:
            return self.filter(project_id=kwargs['project_pk'])

        return self

    def exclude_for_client_report(self):
        return self.filter(~Q(status__in=[self.model.Statuses.NOT_VERIFIED, self.model.Statuses.OUTSTANDING]))
