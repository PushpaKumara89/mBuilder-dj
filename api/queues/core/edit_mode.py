from api.services.edit_mode_entity_service import EditModeEntityService


def remove_user_project_edit_mode(user: int, project: int) -> None:
    EditModeEntityService().remove_user_project_edit_mode(user, project)
