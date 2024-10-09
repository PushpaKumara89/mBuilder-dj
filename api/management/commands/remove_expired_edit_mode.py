import pendulum
from django.core.management.base import BaseCommand
from django.db import connection

from mbuild.settings import EDIT_MODE_CLOSE_IN_MINUTES


class Command(BaseCommand):
    help = "Remove expired edit modes."

    def handle(self, *args, **options):
        time_diff_in_seconds = EDIT_MODE_CLOSE_IN_MINUTES * 60

        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM edit_mode WHERE EXTRACT(EPOCH FROM (%s - updated_at)) > %s
            """, (pendulum.now().to_datetime_string(), time_diff_in_seconds))
