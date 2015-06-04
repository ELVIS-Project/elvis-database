from django.db import models
import pytz

#django signal handlers
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
        return u"{0}".format(self.name)


@receiver(post_save, sender=InstrumentVoice)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_instrument_voice".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    instrument_voice = instance

    #LM: Same ugly bit of code as in all the models, remove when encoding issues are fixed.
    try:
        instrument_voice_name = unicode(instrument_voice.name)
    except UnicodeDecodeError:
        instrument_voice_name = instrument_voice.name.decode('utf-8')

    if instrument_voice.comment is not None:
        try:
            instrument_voice_comment = unicode(instrument_voice.comment)
        except UnicodeDecodeError:
            instrument_voice_comment = instrument_voice.comment.decode('utf-8')
            
    try:
        instrument_voice_created = pytz.utc.localize(instrument_voice.created)
    except ValueError:
        instrument_voice_created = instrument_voice.created


    d = {
            'type': 'elvis_instrument_voice',
            'id': str(uuid.uuid4()),
            'item_id': int(instrument_voice.id),
            'name': instrument_voice_name,
            'instruments_voices': instrument_voice_name,
            'instruments_voices_searchable': instrument_voice_name,
            'created': instrument_voice_created,
            'updated': instrument_voice.updated,
            'comment': instrument_voice_comment,
    }
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
