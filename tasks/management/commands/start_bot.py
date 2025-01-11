from django.core.management import BaseCommand
from tasks.services.telegram_bot import run_bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        run_bot()
