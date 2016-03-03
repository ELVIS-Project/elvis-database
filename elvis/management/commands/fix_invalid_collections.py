from django.core.management import BaseCommand
from django.core.cache import cache
from elvis.models.collection import Collection


class Command(BaseCommand):
    """
    A management command to fix any invalid collection states.
    """
    def handle(self, *args, **options):
        total = 0
        for c in Collection.objects.all():
            for m in c.movements.all():
                if m.piece in c.pieces.all():
                    c.movements.remove(m)
                    total += 1
        print("Fixed {0} invalid collections.".format(total))
