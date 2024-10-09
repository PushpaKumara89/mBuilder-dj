import csv
import uuid
from io import StringIO

import requests
from azure.storage.blob import BlockBlobService
from azure.storage.common import CloudStorageAccount
from django.core.management.base import BaseCommand
from django.db.models import Q
from tabulate import tabulate

from api.models import Project, Task, Subtask
from api.storages import AzureMediaStorage


class Command(BaseCommand):
    help = 'Parse CSVs with status statistics.'

    file_url: str
    parse_tasks: bool
    parse_subtasks: bool
    task_status_header_index: int
    task_id_header_index: int
    subtask_status_header_index: int
    subtask_id_header_index: int
    project_name_header_index: int
    blob_service: BlockBlobService

    def add_arguments(self, parser):
        parser.add_argument('file_url', type=str)
        parser.add_argument('-pt', '--parse-tasks', action='store_true')
        parser.add_argument('-ps', '--parse-subtasks', action='store_true')

    def handle(self, *args, **options):
        self.init(**options)
        download = requests.get(self.file_url)
        decoded_content = download.content.decode('utf-8')
        file_data = csv.reader(decoded_content.splitlines(), delimiter=',')
        header = next(file_data, None)

        try:
            self.project_name_header_index = header.index('ProjectName')
        except ValueError:
            self.stdout.write(self.style.ERROR('ProjectName field not found'))
            return

        file_data = list(file_data)

        try:
            project = Project.objects.filter(
                name=file_data[0][self.project_name_header_index]
            ).get()
        except Project().DoesNotExist:
            self.stdout.write(self.style.ERROR('Project not found'))
            return

        if self.parse_tasks:
            self._parse_tasks(file_data, project, header)
        elif self.parse_subtasks:
            self._parse_subtasks(file_data, project, header)

    def _parse_tasks(self, file_data: list, project: Project, header: list) -> None:
        try:
            self.task_id_header_index = header.index('TaskId')
        except ValueError as e:
            self.stdout.write(self.style.ERROR('TaskId field not found'))
            raise e

        try:
            self.task_status_header_index = header.index('TaskStatus')
        except ValueError as e:
            self.stdout.write(self.style.ERROR('TaskId field not found'))
            raise e

        task_ids = set()
        tasks_with_mismatching_status: list[list] = []
        missing_in_file_tasks_status: list[list] = []
        missing_in_database_tasks: list[list] = []

        for i, row in enumerate(file_data):
            task_id = int(row[self.task_id_header_index])
            task_ids.add(task_id)
            file_task_status = row[self.task_status_header_index]
            try:
                task = Task.objects.filter(id=task_id).get()
            except Task().DoesNotExist:
                missing_in_database_tasks.append([task_id, project.name])
                print(f'Task with id {task_id} does not exists.')
                continue

            if task.status != file_task_status:
                tasks_with_mismatching_status.append([
                    task_id,
                    project.name,
                    task.status,
                    file_task_status
                ])

        tasks = Task.objects.filter(~Q(id__in=task_ids), project=project)
        for task in tasks:
            missing_in_file_tasks_status.append([
                task.id,
                task.status,
                project.name
            ])

        print("\n"*2)
        print('Tasks with mismatching statuses')
        print("\n"*2)

        tasks_with_mismatching_status_headers = ['QCTId', 'ProjectName', 'DatabaseStatus', 'ExcelFileStatus']
        print(tabulate(tasks_with_mismatching_status, headers=tasks_with_mismatching_status_headers, tablefmt='github'))

        print("\n"*2)
        print('Tasks missing in Excel file')
        print("\n"*2)

        missing_in_file_tasks_status_headers = ['QCTId', 'DatabaseStatus', 'ProjectName']
        print(tabulate(missing_in_file_tasks_status, headers=missing_in_file_tasks_status_headers, tablefmt='github'))

        print("\n"*2)
        print('Tasks not found in database')
        print("\n"*2)

        missing_in_database_tasks_headers = ['QCTId', 'ProjectName']
        print(tabulate(missing_in_database_tasks, headers=missing_in_database_tasks_headers, tablefmt='github'))

        self.save_tasks_with_mismatching_statuses(tasks_with_mismatching_status, tasks_with_mismatching_status_headers)
        self.save_missing_in_file_tasks(missing_in_file_tasks_status, missing_in_file_tasks_status_headers)
        self.save_missing_in_database_tasks(missing_in_database_tasks, missing_in_database_tasks_headers)

    def _parse_subtasks(self, file_data: list, project: Project, header: list) -> None:
        try:
            self.subtask_id_header_index = header.index('SubTaskBkId')
        except ValueError as e:
            self.stdout.write(self.style.ERROR('SubtaskId field not found'))
            raise e

        try:
            self.subtask_status_header_index = header.index('SubTaskStatus')
        except ValueError as e:
            self.stdout.write(self.style.ERROR('SubTaskStatus field not found'))
            raise e

        subtask_ids = set()
        subtasks_with_mismatching_status: list[list] = []
        missing_in_file_subtasks: list[list] = []
        missing_in_database_subtasks: list[list] = []

        for i, row in enumerate(file_data):
            subtask_id = int(row[self.subtask_id_header_index])
            subtask_ids.add(subtask_id)
            file_subtask_status = row[self.subtask_status_header_index]
            try:
                subtask = Subtask.objects.filter(id=subtask_id).get()
            except Subtask().DoesNotExist:
                missing_in_database_subtasks.append([subtask_id, project.name])
                print(f'Task with id {subtask_id} does not exists.')
                continue

            if subtask.status != file_subtask_status:
                subtasks_with_mismatching_status.append([
                    subtask_id,
                    project.name,
                    subtask.status,
                    file_subtask_status
                ])

        subtasks = Subtask.objects.filter(
            ~Q(id__in=subtask_ids),
            task__project=project
        )

        for subtask in subtasks:
            missing_in_file_subtasks.append([
                subtask.id,
                subtask.status,
                project.name
            ])

        print("\n" * 2)
        print('Subtask with mismatching statuses')
        print("\n" * 2)

        subtasks_with_mismatching_status_headers = ['SubTaskId', 'ProjectName', 'DatabaseStatus', 'ExcelFileStatus']
        print(tabulate(subtasks_with_mismatching_status, headers=subtasks_with_mismatching_status_headers, tablefmt='github'))

        print("\n" * 2)
        print('Subtasks missing in Excel file')
        print("\n" * 2)

        missing_in_file_subtasks_headers = ['SubTaskId', 'DatabaseStatus', 'ProjectName']
        print(tabulate(missing_in_file_subtasks, headers=missing_in_file_subtasks_headers, tablefmt='github'))

        print("\n" * 2)
        print('Subtasks missing in database')
        print("\n" * 2)

        missing_in_database_subtasks_headers = ['SubTaskId', 'ProjectName']
        print(tabulate(missing_in_database_subtasks, headers=missing_in_database_subtasks_headers, tablefmt='github'))

        self.save_subtasks_with_mismatching_statuses(subtasks_with_mismatching_status, subtasks_with_mismatching_status_headers)
        self.save_missing_in_file_subtasks(missing_in_file_subtasks, missing_in_file_subtasks_headers)
        self.save_missing_in_database_subtasks(missing_in_database_subtasks, missing_in_database_subtasks_headers)

    def save_subtasks_with_mismatching_statuses(self, subtasks_with_mismatching_status: list[list], headers: list[str]) -> None:
        print('Save subtasks with mismatching status')

        filename = f'subtasks_with_mismatching_statuses_{uuid.uuid4()}.csv'
        self.save_csv(subtasks_with_mismatching_status, headers, filename)

    def save_missing_in_file_subtasks(self, missing_subtasks_status: list[list], headers: list[str]) -> None:
        print('Save missing in file subtasks')

        filename = f'missing_in_file_subtasks_{uuid.uuid4()}.csv'
        self.save_csv(missing_subtasks_status, headers, filename)

    def save_missing_in_database_subtasks(self, missing_subtasks_status: list[list], headers: list[str]) -> None:
        print('Save missing in database subtasks')

        filename = f'missing_in_database_subtasks_{uuid.uuid4()}.csv'
        self.save_csv(missing_subtasks_status, headers, filename)

    def save_tasks_with_mismatching_statuses(self, subtasks_with_mismatching_status: list[list], headers: list[str]) -> None:
        print('Save tasks with mismatching status')

        filename = f'tasks_with_mismatching_statuses_{uuid.uuid4()}.csv'
        self.save_csv(subtasks_with_mismatching_status, headers, filename)

    def save_missing_in_file_tasks(self, missing_in_file_tasks: list[list], headers: list[str]) -> None:
        print('Save missing in file tasks')

        filename = f'missing_in_file_tasks_{uuid.uuid4()}.csv'
        self.save_csv(missing_in_file_tasks, headers, filename)

    def save_missing_in_database_tasks(self, missing_in_database_tasks: list[list], headers: list[str]) -> None:
        print('Save missing in database tasks')

        filename = f'missing_in_database_tasks_{uuid.uuid4()}.csv'
        self.save_csv(missing_in_database_tasks, headers, filename)

    def save_csv(self, rows: list[list], headers: list[str], filename: str) -> None:
        f = StringIO()
        write = csv.writer(f)
        write.writerow(headers)
        write.writerows(rows)

        self.blob_service.create_blob_from_bytes(
            container_name=AzureMediaStorage.azure_container,
            blob_name=filename,
            blob=f.getvalue().encode()
        )
        f.close()

        print(f'Filename is {filename}')

    def init(self, **options) -> None:
        self.file_url = options['file_url']
        self.parse_tasks = options['parse_tasks']
        self.parse_subtasks = options['parse_subtasks']

        storage_account = CloudStorageAccount(
            account_name=AzureMediaStorage.account_name,
            account_key=AzureMediaStorage.account_key
        )
        self.blob_service = storage_account.create_block_blob_service()
