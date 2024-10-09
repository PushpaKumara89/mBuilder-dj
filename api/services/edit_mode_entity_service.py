import pendulum

from api.models import EditMode
from api.services.base_entity_service import BaseEntityService
from mbuild.settings import EDIT_MODE_CLOSE_IN_MINUTES


class EditModeEntityService(BaseEntityService):
    model = EditMode

    def remove_user_project_edit_mode(self, user: int, project: int) -> None:
        filters = {'user': user, 'project': project}
        edit_mode = EditMode.objects.filter(**filters).first()

        time_diff_top_limit = EDIT_MODE_CLOSE_IN_MINUTES * 60
        if edit_mode and (pendulum.now() - edit_mode.updated_at).in_seconds() > time_diff_top_limit:
            EditMode.objects.filter(**filters).delete()
