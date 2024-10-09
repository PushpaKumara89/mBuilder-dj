import json
from operator import itemgetter

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Min
from reversion.models import Version

from api.models import FloorPlan, FloorPlanRevisionMeta, FloorPlanArea


class Command(BaseCommand):
    help = "Add missing floor plan revision meta."

    def handle(self, *args, **options):
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        floor_plan_area_content_type = ContentType.objects.get_for_model(FloorPlanArea)

        self.add_meta_for_floor_plan_revision_versions(floor_plan_content_type)
        self.add_meta_for_floor_plan_area_revision_versions(floor_plan_content_type, floor_plan_area_content_type)
        self.add_meta_for_first_floor_plan_revisions(floor_plan_content_type)

    def add_meta_for_first_floor_plan_revisions(self, floor_plan_content_type: ContentType) -> None:
        versions_with_first_revision = Version.objects.values('object_id').annotate(first_revision_id=Min('revision_id')).filter(
            content_type=floor_plan_content_type,
        ).values_list('first_revision_id', flat=True)

        meta = map(
            lambda revision_id: FloorPlanRevisionMeta(
                event_type=FloorPlanRevisionMeta.EventTypes.FILE_UPLOADED.value,
                revision_id=revision_id
            ),
            versions_with_first_revision
        )

        FloorPlanRevisionMeta.objects.bulk_create(meta, 100)

    def add_meta_for_floor_plan_revision_versions(self, floor_plan_content_type: ContentType) -> None:
        floor_plans_with_changes = Version.objects.values('object_id').annotate(versions_count=Count('id')).filter(content_type=floor_plan_content_type, versions_count__gt=1).order_by()
        for floor_plan_version in floor_plans_with_changes:
            versions = Version.objects.filter(
                object_id=floor_plan_version['object_id'],
                content_type=floor_plan_content_type
            ).order_by('-id')

            for index, version in enumerate(versions):
                try:
                    previous_version = versions[index + 1:index + 2][0]
                except IndexError:
                    break

                serialized_data = json.loads(version.serialized_data)[0]
                previous_version_serialized_data = json.loads(previous_version.serialized_data)[0]
                current_version_media = serialized_data['fields']['media']
                previous_version_media = previous_version_serialized_data['fields']['media']

                if current_version_media != previous_version_media:
                    is_floor_plan_meta_missing = not FloorPlanRevisionMeta.objects.filter(
                        revision_id=version.revision_id,
                        event_type=FloorPlanRevisionMeta.EventTypes.FILE_UPDATED.value
                    ).exists()

                    if is_floor_plan_meta_missing:
                        FloorPlanRevisionMeta.objects.create(
                            revision_id=version.revision_id,
                            event_type=FloorPlanRevisionMeta.EventTypes.FILE_UPDATED.value
                        )

    def add_meta_for_floor_plan_area_revision_versions(
            self,
            floor_plan_content_type: ContentType,
            floor_plan_area_content_type: ContentType,
    ) -> None:
        self.add_meta_for_updated_and_deleted_floor_plan_area_revision_versions(floor_plan_area_content_type)
        self.add_meta_for_created_floor_plan_area_revision_versions(
            floor_plan_content_type,
            floor_plan_area_content_type
        )

    def add_meta_for_created_floor_plan_area_revision_versions(
            self,
            floor_plan_content_type: ContentType,
            floor_plan_area_content_type: ContentType,
    ):
        floor_plan_versions = Version.objects.values('object_id').annotate(versions_count=Count('id')).filter(
            content_type=floor_plan_content_type,
            versions_count__gt=1
        ).order_by()

        for floor_plan_version in floor_plan_versions:
            versions = Version.objects.annotate(areas_count=Count('revision__version__id', filter=Q(
                revision__version__content_type=floor_plan_area_content_type
            ))).filter(
                content_type=floor_plan_content_type,
                object_id=floor_plan_version['object_id']
            ).order_by('-id')

            for index, version in enumerate(versions):
                try:
                    previous_version = versions[index + 1:index + 2][0]
                except IndexError:
                    break

                if version.areas_count > previous_version.areas_count:
                    is_floor_plan_meta_missing = not FloorPlanRevisionMeta.objects.filter(
                        revision_id=version.revision_id,
                        event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value
                    ).exists()

                    if is_floor_plan_meta_missing:
                        FloorPlanRevisionMeta.objects.create(
                            revision_id=version.revision_id,
                            event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value
                        )

    def add_meta_for_updated_and_deleted_floor_plan_area_revision_versions(self, floor_plan_area_content_type: ContentType):
        floor_plan_areas_with_changes = Version.objects.values('object_id').annotate(versions_count=Count('id')).filter(
            content_type=floor_plan_area_content_type, versions_count__gt=1
        ).order_by()

        for floor_plan_area_version in floor_plan_areas_with_changes:
            versions = Version.objects.filter(
                object_id=floor_plan_area_version['object_id'],
                content_type=floor_plan_area_content_type
            ).order_by('-id')

            for index, version in enumerate(versions):
                try:
                    previous_version = versions[index + 1:index + 2][0]
                except IndexError:
                    break

                serialized_data = json.loads(version.serialized_data)[0]
                previous_version_serialized_data = json.loads(previous_version.serialized_data)[0]
                current_version_data = itemgetter('area', 'polygon', 'deleted')(serialized_data['fields'])
                previous_version_data = itemgetter('area', 'polygon', 'deleted')(previous_version_serialized_data['fields'])

                if current_version_data != previous_version_data:
                    is_floor_plan_meta_missing = not FloorPlanRevisionMeta.objects.filter(
                        revision_id=version.revision_id,
                        event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value
                    ).exists()

                    if is_floor_plan_meta_missing:
                        FloorPlanRevisionMeta.objects.create(
                            revision_id=version.revision_id,
                            event_type=FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value
                        )
