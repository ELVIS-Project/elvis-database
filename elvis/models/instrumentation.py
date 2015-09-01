from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from elvis.models.main import ElvisModel


class InstrumentVoice(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

@receiver(post_save, sender=InstrumentVoice)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_instrument_voice".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    instrument_voice = instance

    d = {'type': 'elvis_instrument_voice',
         'id': str(uuid.uuid4()),
         'item_id': int(instrument_voice.id),
         'name': instrument_voice.name,
         'instruments_voices_searchable': instrument_voice.name,
         'created': instrument_voice.created,
         'updated': instrument_voice.updated,
         'comment': instrument_voice.comment}
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=InstrumentVoice)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_instrument_voice".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
