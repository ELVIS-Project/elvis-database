import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.main import ElvisModel


class Genre(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        genre = self

        return {'type': 'elvis_genre',
                'id': str(uuid.uuid4()),
                'item_id': int(genre.id),
                'name': genre.name,
                'genres_searchable': genre.name,
                'created': genre.created,
                'updated': genre.updated,
                'comment': genre.comment}


@receiver(post_save, sender=Genre)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Genre)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
