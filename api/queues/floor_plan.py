from api.models import LocationMatrix
from api.queues.core.base import use_rq_if_configured
from api.queues.celery.floor_plan import update_floor_plan_with_areas as update_floor_plan_with_areas_celery
from api.queues.rq.floor_plan import update_floor_plan_with_areas as update_floor_plan_with_areas_rq


@use_rq_if_configured(update_floor_plan_with_areas_rq)
def update_floor_plan_with_areas(location_matrices: list[LocationMatrix], updated_data: list[dict]) -> None:
    update_floor_plan_with_areas_celery.delay(location_matrices, updated_data)
