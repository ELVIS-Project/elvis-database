from django.core.management import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    """
    A management command to clear the cache.
    """
    def handle(self, *args, **options):
        cache.clear()
        print("Successfully cleared cache.")
