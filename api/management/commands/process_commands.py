from django.core.management.base import BaseCommand

from api.commands import process_commands
from api.models import Command as CommandModel


class Command(BaseCommand):
    help = "Process commands to create, delete, or change entity."

    def handle(self, *args, **options):
        commands = CommandModel.objects(status=CommandModel.Statuses.PENDING.value).order_by('created_at')[:100]
        process_commands(commands)
