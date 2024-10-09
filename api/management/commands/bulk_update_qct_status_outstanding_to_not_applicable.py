import csv

import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now
from typing import List

from api.models import Task, TaskUpdate


User = get_user_model()


class Command(BaseCommand):
    help = 'Bulk Update Quality Critical Tasks for the ONE NINE ELMS'
    _cache_key = 'qst_status_change_task_id_{}'

    def add_arguments(self, parser):
        parser.add_argument('file_url', type=str)
        parser.add_argument('-bs', '--batch_size', nargs='?', type=int, default=1000)
        parser.add_argument('-ue', '--user_email', nargs='?', type=str, default='anthony.konfos@multiplex.global')

    def _create_and_update_task(self, batch_tasks: List):
        with transaction.atomic():
            TaskUpdate.objects.bulk_create(batch_tasks)
            Task.objects.filter(id__in=[tu.task_id for tu in batch_tasks]).update(status=Task.Statuses.NOT_APPLICABLE, updated_at=now())
            for tu in batch_tasks:
                cache.add(self._cache_key.format(tu.task_id), 0, ((60 * 60 * 24) * (7 * 4)))

    def handle(self, *args, **options):
        file_url = options['file_url']
        user = User.objects.get(email=options['user_email'])
        batch_size = options['batch_size']

        with requests.Session() as s:
            download = s.get(file_url)
            decoded_content = download.content.decode('utf-8')
            file_data = csv.reader(decoded_content.splitlines(), delimiter=',')
            batch_tasks = []
            task_ids = set()

            for i, row in enumerate(list(file_data)):
                if i == 0:
                    continue

                status = row[0].lower().strip()
                task_id = int(row[1].replace('QCT-', ''))
                cache_key = self._cache_key.format(task_id)
                if status == Task.Statuses.OUTSTANDING and task_id not in task_ids and cache.get(cache_key, None) is None:
                    task_ids.add(task_id)
                    batch_tasks.append(
                        TaskUpdate(task_id=task_id,
                                   user_id=user.id,
                                   old_data={'status': Task.Statuses.OUTSTANDING},
                                   new_data={'status': Task.Statuses.NOT_APPLICABLE})
                    )

                if i % batch_size == 0 and batch_tasks:
                    self._create_and_update_task(batch_tasks)
                    batch_tasks = []

            if batch_tasks:
                self._create_and_update_task(batch_tasks)
