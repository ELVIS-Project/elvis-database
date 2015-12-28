import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.elvis_model import ElvisModel


class Tag(ElvisModel):
    class Meta:
        app_label = "elvis"

    def solr_dict(self):
        tag = self

        return {'type': 'elvis_tag',
                'id': int(tag.id),
                'name': tag.title,
                'tags': tag.title,
                'tags_searchable': tag.title}


@receiver(post_save, sender=Tag)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Tag)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)