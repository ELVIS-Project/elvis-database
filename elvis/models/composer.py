import datetime
import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.main import ElvisModel


class Composer(ElvisModel):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    birth_date = models.IntegerField(blank=True, null=True)
    death_date = models.IntegerField(blank=True, null=True)

    @property
    def piece_count(self):
        return self.pieces.all().count()

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()

    def solr_dict(self):
        composer = self
        if composer.birth_date:
            birth = datetime.date(composer.birth_date, 1, 1)
        else:
            birth = None
        if composer.death_date:
            death = datetime.date(composer.death_date, 1, 1)
        else:
            death = None

        return {'type': 'elvis_composer',
                'id': str(uuid.uuid4()),
                'item_id': int(composer.id),
                'name': composer.name,
                'birth_date': birth,
                'death_date': death,
                'created': composer.created,
                'updated': composer.updated,
                'composers_searchable': composer.name}


@receiver(post_save, sender=Composer)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Composer)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
