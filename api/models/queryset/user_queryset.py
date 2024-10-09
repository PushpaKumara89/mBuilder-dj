from django.db.models import Subquery, OuterRef, BooleanField

from api.models.queryset import SafeDeleteQueryset


class UserQueryset(SafeDeleteQueryset):
    def add_notifications_enabled(self, project):
        from api.models import ProjectUser
        return self.annotate(
            is_notifications_enabled=Subquery(
                (ProjectUser.objects
                 .filter(project=project, user=OuterRef('pk'))
                 .values('is_notifications_enabled'))[:1],
                output_field=BooleanField()
            )
        )
