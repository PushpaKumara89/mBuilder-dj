from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class DifferentPasswordValidator:
    def validate(self, password, user=None):
        if user is not None and user.check_password(password):
            raise ValidationError(
                _("You've used that password before. Please choose a different one."),
                code='password_the_same'
            )

    def get_help_text(self):
        return _("The password must be different from the current one")
