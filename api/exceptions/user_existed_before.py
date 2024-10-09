from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from api.exceptions.conflict import Conflict


class UserExistedBefore(Conflict):
    default_detail = _('User with email "{email}" existed in the system before.')

    def __init__(self, email):
        detail = force_str(self.default_detail).format(email=email)
        super().__init__(detail=detail)

