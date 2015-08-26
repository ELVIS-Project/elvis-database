from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class InstrumentVoice(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{0}".format(self.name)


@receiver(post_save, sender=InstrumentVoice)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import scorched
    from django.conf import settings

    solrconn = scorched.SolrInterface(settings.SOLR_SERVER)
    response = solrconn.query(item_id=instance.id, type="elvis_instrument_voice").execute()
    if response.result.docs:
        solrconn.delete_by_ids(response[0]['id'])

    instrument_voice = instance

    d = {'type': 'elvis_instrument_voice',
         'id': str(uuid.uuid4()),
         'item_id': int(instrument_voice.id),
         'name': instrument_voice.name,
         'instruments_voices_searchable': instrument_voice.name,
         'created': instrument_voice.created,
         'updated': instrument_voice.updated,
         'comment': instrument_voice.comment}
    solrconn.add(d)
    solrconn.commit()


@receiver(post_delete, sender=InstrumentVoice)
def solr_delete(sender, instance, **kwargs):
    import scorched
    from django.conf import settings

    solrconn = scorched.SolrInterface(settings.SOLR_SERVER)
    response = solrconn.query(item_id=instance.id, type="elvis_instrument_voice").execute()
    if response.result.docs:
        solrconn.delete_by_ids(response[0]['id'])
        solrconn.commit()
