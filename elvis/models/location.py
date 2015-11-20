import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.main import ElvisModel


class Location(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        location = self

        return {'type': 'elvis_location',
                'id': str(uuid.uuid4()),
                'item_id': int(location.id),
                'name': location.name,
                'locations_searchable': location.name,
                'created': location.created,
                'updated': location.updated,
                'comment': location.comment}


class Place(Location):
    class Meta:
        proxy = True


@receiver(post_save, sender=Location)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Location)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
