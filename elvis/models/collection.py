import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.main import ElvisModel


class Collection(ElvisModel):
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "collections"
        app_label = "elvis"

    public = models.NullBooleanField(blank=True)

    def __unicode__(self):
        return "{0}".format(self.title)

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
        collection = self
        if collection.creator:
            creator_name = collection.creator.username
        else:
            creator_name = None

        return {'type': 'elvis_collection',
                'id': str(uuid.uuid4()),
                'item_id': int(collection.id),
                'title': collection.title,
                'created': collection.created,
                'updated': collection.updated,
                'comment': collection.comment,
                'creator_name': creator_name,
                'collections_searchable': collection.title}


@receiver(post_save, sender=Collection)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Collection)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)