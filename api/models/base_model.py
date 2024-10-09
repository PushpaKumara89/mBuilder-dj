from django.db.models import DateTimeField
from django.utils.text import camel_case_to_spaces
from safedelete.models import SafeDeleteModel

from api.models.managers import BaseManager, BaseAllManager, BaseDeletedManager


class BaseModel(SafeDeleteModel):
    create_events_on_update = True

    class Meta:
        abstract = True
        ordering = ['id']

    objects = BaseManager()
    all_objects = BaseAllManager()
    deleted_objects = BaseDeletedManager()

    created_at = DateTimeField(auto_now_add=True, null=False, editable=False, blank=False)
    updated_at = DateTimeField(auto_now=True, null=False, editable=False, blank=False)

    def save(self, keep_deleted=False, **kwargs):
        from api.models import User
        creation = kwargs.pop('creation', False)

        def is_not_deletion_and_creation_of_model():
            return not keep_deleted and not self.deleted and not creation and self.pk

        # Add this exception to avoid critical error for password reset in django_rest_passwordreset.views:113.
        def is_not_user_password_update():
            return self.__class__ != User or (self.__class__ == User and not self._password)

        if is_not_deletion_and_creation_of_model() and is_not_user_password_update():
            assert kwargs.get('update_fields'), (
                "You have to pass `update_fields` argument."
                "This argument helps us in determination of Event type."
            )

        super().save(keep_deleted, **kwargs)

    def get_snake_case_class_name(self):
        return '_'.join(camel_case_to_spaces(self.__class__.__name__).split(' '))
