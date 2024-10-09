from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey


class Command(BaseCommand):
    help = "Generate API key."

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        name = options['name']
        api_key, key = APIKey.objects.create_key(name=name)
        self.stdout.write(self.style.WARNING('Key %s was generated for %s' % (key, name)))
