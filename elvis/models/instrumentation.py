import uuid

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.main import ElvisModel


class InstrumentVoice(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        instrument_voice = self

        return {'type': 'elvis_instrument_voice',
                'id': str(uuid.uuid4()),
                'item_id': int(instrument_voice.id),
                'name': instrument_voice.name,
                'instruments_voices_searchable': instrument_voice.name,
                'created': instrument_voice.created,
                'updated': instrument_voice.updated,
                'comment': instrument_voice.comment}


@receiver(post_save, sender=InstrumentVoice)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=InstrumentVoice)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
