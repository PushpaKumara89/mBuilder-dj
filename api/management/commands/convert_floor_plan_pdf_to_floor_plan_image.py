from django.core.management.base import BaseCommand
from sentry_sdk import capture_exception

from api.models import FloorPlan, Media
from api.models.floor_plan_image import FloorPlanImage
from api.services.floor_plan_image_entity_service import FloorPlanImageEntityService


class Command(BaseCommand):
    def handle(self, *args, **options):
        floor_plan = FloorPlan.objects.values_list('media_id', flat=True)
        floor_plan_image = FloorPlanImage.objects.values_list('plan_id', flat=True)
        plan_media = Media.objects.filter(id__in=set(floor_plan) - set(floor_plan_image))
        service = FloorPlanImageEntityService()

        for media in plan_media:
            if media.is_pdf:
                try:
                    service.create({'media': media})
                except Exception as e:
                    capture_exception(e)
