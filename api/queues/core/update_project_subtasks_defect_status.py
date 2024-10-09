import pendulum

from api.models import Subtask


def update_project_subtasks_defect_status(project_id, project_completion_date: str):
    project_completion_date = pendulum.parse(project_completion_date)

    if pendulum.now().diff(project_completion_date, False).in_days() <= 0:
        Subtask.all_objects.filter(task__location_matrix__project_id=project_id, is_defect=False).update(is_defect=True)
    else:
        Subtask.all_objects.filter(task__location_matrix__project_id=project_id, is_defect=True).update(is_defect=False)
