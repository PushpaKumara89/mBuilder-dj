from api.models.queryset import SafeDeleteQueryset


class ProjectQueryset(SafeDeleteQueryset):
    def filter_by_user_permissions(self, user):
        if not user.is_company_admin and not user.is_superuser:
            return self.filter(users__pk=user.pk)
        return self
