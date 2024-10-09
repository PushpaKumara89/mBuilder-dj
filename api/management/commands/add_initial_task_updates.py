from django.core.management.base import BaseCommand

from api.models import Task, TaskUpdate


class Command(BaseCommand):
    help = "Create initial task updates."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Start creating initial task updates.'))
        tasks_without_updates = Task.all_objects.filter(taskupdate__isnull=True).all()
        tasks_count = tasks_without_updates.count()
        self.stdout.write(self.style.WARNING(f'Updates needed for {tasks_count} updates.'))

        for task in tasks_without_updates:
            self.stdout.write(self.style.WARNING(f'Create update for task {task.id}.'))
            TaskUpdate.objects.create(**{
                'user': task.user,
                'task': task,
                'old_data': {},
                'new_data': {
                    'status': task.status
                }
            })
            self.stdout.write(self.style.WARNING(f'Update for task {task.id} has been created.'))

        self.stdout.write(self.style.WARNING(f'Initial updates has been created for {tasks_count} tasks.'))
