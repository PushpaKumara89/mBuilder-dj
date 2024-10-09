import reversion
from reversion.models import Version

from api.models import FloorPlan, FloorPlanRevisionMeta, User
from api.models.floor_plan_revision import FloorPlanRevision
from api.services.base_entity_service import BaseEntityService


class FloorPlanRevisionEntityService(BaseEntityService):
    model = FloorPlanRevision

    def revert_revision(self, floor_plan_id: int, revision_id: int, user: User):
        floor_plan = FloorPlan.all_objects.filter(pk=floor_plan_id).get()
        last_floor_plan_revision = Version.objects.get_for_object(floor_plan)[0].revision_id

        if last_floor_plan_revision == revision_id:
            return

        with reversion.create_revision():
            revision = self.model.objects.filter(pk=revision_id).prefetch_related('floorplanrevisionmeta_set').get()
            revision.revert(delete=True)
            reversion.set_user(user)
            for revision_meta in revision.floorplanrevisionmeta_set.all():
                reversion.add_meta(FloorPlanRevisionMeta, event_type=revision_meta.event_type)

        return revision
