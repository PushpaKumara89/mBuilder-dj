from django.contrib.contenttypes.models import ContentType
from reversion.models import Revision as BaseRevision, Version

from api.models import FloorPlan, FloorPlanArea


class FloorPlanRevision(BaseRevision):
    class Meta:
        proxy = True

    def floor_plan(self):
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        return Version.objects.filter(
            revision=self.id,
            content_type=floor_plan_content_type,
            serialized_data__regex=r'("deleted": null).'
        ).first()

    def floor_plan_areas(self):
        floor_plan_area_content_type = ContentType.objects.get_for_model(FloorPlanArea)
        return Version.objects.filter(
            revision=self.id,
            content_type=floor_plan_area_content_type,
            serialized_data__regex=r'("deleted": null).'
        )
