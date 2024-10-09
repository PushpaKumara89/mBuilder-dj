from django.contrib.auth.models import AnonymousUser as DjangoAnonymousUser


class AnonymousUser(DjangoAnonymousUser):
    def __init__(self):
        super(AnonymousUser, self).__init__()

    @property
    def is_company_admin(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def is_manager(self):
        return False

    @property
    def is_subcontractor(self):
        return False

    @property
    def is_client(self):
        return False

    @property
    def is_consultant(self):
        return False

    def save(self):
        pass

    def delete(self):
        pass

    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        pass
