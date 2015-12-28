import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.elvis_model import ElvisModel


class Language(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        language = self

        return {'type': 'elvis_language',
                'id': int(language.id),
                'name': language.name,
                'languages_searchable': language.name,
                'created': language.created,
                'updated': language.updated,
                'comment': language.comment}


@receiver(post_save, sender=Language)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Language)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)