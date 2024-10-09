from typing import Callable, Any

from mbuild.settings.common import ENV
from mbuild.settings.rq_queues import AVAILABLE_ENVS as RQ_ENVS


def use_rq_if_configured(task_rq: Callable[..., Any]) -> Callable[..., None]:
    def wrapper(func: Callable[..., None]) -> Callable[..., None]:
        def wrapped(*args, **kwargs) -> None:
            if ENV in RQ_ENVS:
                task_rq.delay(*args, **kwargs)
            else:
                func(*args, **kwargs)
        return wrapped
    return wrapper
