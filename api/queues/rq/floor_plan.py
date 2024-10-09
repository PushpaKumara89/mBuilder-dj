from django_rq import job

from api.models import LocationMatrix
from api.queues.core.floor_plan import update_floor_plan_with_areas as update_floor_plan_with_area_core


@job('floor_plan', timeout=3600)
def update_floor_plan_with_areas(location_matrices: list[LocationMatrix], update_data: list[dict]) -> None:
    update_floor_plan_with_area_core(location_matrices, update_data)
