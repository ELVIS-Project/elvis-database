import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.elvis_model import ElvisModel


class Source(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        source = self

        return {'type': 'elvis_source',
                'id': int(source.id),
                'title': source.name,
                'sources_searchable': source.name,
                'created': source.created,
                'updated': source.updated}


@receiver(post_save, sender=Source)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Source)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)