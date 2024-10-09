import pendulum
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Q

from api.models import Media
from api.services.media_entity_service import MediaEntityService


class Command(BaseCommand):
    help = "Create thumbnails for existing media."

    def handle(self, *args, **options):
        ttl = 60 * 60 * 24 * 7
        offset_key = 'thumbnails_creation_offset'
        offset = cache.get(offset_key, 0)
        limit = offset + 100
        cache_key = 'media:%s:thumbnails-created'

        self._log_message('Thumbnails creation has been started.')

        while True:
            media = Media.all_objects.filter(
                Q(assethandoverdocumentmedia__isnull=False)
                | Q(locationmatrixpackage__isnull=False)
                | Q(packageactivity__isnull=False)
                | Q(packagehandoverdocumentmedia__isnull=False)
                | Q(qualityissue__isnull=False)
                | Q(qualityissueupdate__isnull=False)
                | Q(subtask__isnull=False)
                | Q(subtaskupdate__isnull=False)
                | Q(taskupdate__isnull=False),
                name__endswith='pdf'
            ).order_by('id')[offset:limit]

            if not media:
                self._log_message('There are no media without thumbnails found.')
                break

            for file in media:
                if cache.get(cache_key % file.id):
                    self._log_message(f'Media {file.id} already migrated.')
                    continue

                self._log_message(f'Thumbnails creation for media {file.id} has been started.')
                MediaEntityService().create_thumbnails(file)
                self._log_message(f'Thumbnails for media {file.id} have been created.')

                cache.set(cache_key % file.id, 1, ttl)

            offset += limit
            limit += offset

            cache.set(offset_key, offset, ttl)

            self._log_message(f'Going to the next {limit} media.')

        self._log_message('Thumbnails creation has been finished.')

    def _log_message(self, text: str) -> None:
        self.stdout.write(self.style.WARNING(f'{pendulum.now().to_datetime_string()}: ' + text))
