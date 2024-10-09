from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fill field size for media thumbnails."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE media_thumbnails mt
                SET width=m.sizes[1]::int,
                    height=m.sizes[2]::int
                FROM (SELECT *, string_to_array(substring(media.name FROM '^[1-9]+x[1-9]+'), 'x') AS sizes FROM media) AS m
                WHERE m.id = mt.thumbnail_id
                  AND (mt.width IS NULL OR mt.height IS NULL)
            """)
