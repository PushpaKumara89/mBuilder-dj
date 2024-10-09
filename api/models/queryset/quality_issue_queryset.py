from django.db.models import Case, IntegerField, QuerySet, Q
from safedelete.queryset import SafeDeleteQueryset

from api.models.queryset.utilites.make_expressions import numerate_when_expressions
from api.utilities.location_matrix_utilities import annotate_location_matrix_level_parts


class QualityIssueQuerySet(SafeDeleteQueryset):
    def default_order(self, user, query_params) -> QuerySet:
        order_fields = ['location_matrix__building', '-level_number', 'level_postfix', 'location_matrix__area', 'id']
        is_default_sort = 'default_sort' in query_params.getlist('sort') or []

        if user.is_staff and is_default_sort:
            qs = annotate_location_matrix_level_parts(self, 'location_matrix__level')
            when_expressions = numerate_when_expressions([Q(status=self.model.Status.UNDER_REVIEW),
                                                          Q(status=self.model.Status.REQUESTED_APPROVAL_REJECTED),
                                                          Q(status=self.model.Status.UNDER_INSPECTION),
                                                          Q(status=self.model.Status.DECLINED),
                                                          Q(status=self.model.Status.IN_PROGRESS),
                                                          Q(status=self.model.Status.INSPECTION_REJECTED),
                                                          Q(status=self.model.Status.REQUESTING_APPROVAL),
                                                          Q(status=self.model.Status.CONTESTED),
                                                          Q(status=self.model.Status.CLOSED),
                                                          Q(status=self.model.Status.REMOVED)])
            return qs.annotate(status_weight=Case(*when_expressions, default=100, output_field=IntegerField())).order_by('status_weight', *order_fields)
        elif (user.is_client or user.is_consultant) and is_default_sort:
            qs = annotate_location_matrix_level_parts(self, 'location_matrix__level')
            when_expressions = numerate_when_expressions([Q(status=self.model.Status.CONTESTED),
                                                          Q(status=self.model.Status.REQUESTING_APPROVAL),
                                                          Q(status=self.model.Status.UNDER_REVIEW),
                                                          Q(status=self.model.Status.REQUESTED_APPROVAL_REJECTED),
                                                          Q(status=self.model.Status.UNDER_INSPECTION),
                                                          Q(status=self.model.Status.DECLINED),
                                                          Q(status=self.model.Status.IN_PROGRESS),
                                                          Q(status=self.model.Status.INSPECTION_REJECTED),
                                                          Q(status=self.model.Status.CLOSED),
                                                          Q(status=self.model.Status.REMOVED)])
            return qs.annotate(status_weight=Case(*when_expressions, default=100, output_field=IntegerField())).order_by('status_weight', *order_fields)

        return self.all()
