from api.models import LocationMatrix, FloorPlanArea, FloorPlan


def update_floor_plan_with_areas(location_matrices: list[LocationMatrix], update_data: list[dict]) -> None:
    for location_matrix in location_matrices:
        updating_data = next(filter(lambda data: data['id'] == location_matrix.id, update_data))
        building, level, area = location_matrix.building, location_matrix.level, location_matrix.area
        FloorPlanArea.objects.filter(
            floor_plan__building=building,
            floor_plan__level=level,
            area=area
        ).update(area=updating_data['area'])
        FloorPlan.objects.filter(building=building, level=level).update(building=updating_data['building'], level=updating_data['level'])
