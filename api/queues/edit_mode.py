import django_rq
from datetime import timedelta

from api.queues.rq.edit_mode import remove_user_project_edit_mode as remove_user_project_edit_mode_rq
from mbuild.settings.common import ENV
from mbuild.settings.rq_queues import AVAILABLE_ENVS as RQ_ENVS


def schedule_remove_user_project_edit_mode(user_pk: int, project_pk: int, delay_seconds: int = 0) -> None:
    if ENV in RQ_ENVS:
        django_rq.get_queue('edit_mode').enqueue_in(
            timedelta(seconds=delay_seconds),
            remove_user_project_edit_mode_rq,
            user_pk,
            project_pk
        )
