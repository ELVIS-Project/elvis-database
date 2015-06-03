from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from datetime import datetime
import pytz

class Source(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)



@receiver(post_save, sender=Source)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_source".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    source = instance

    #LM: Same ugly bit of code as in all the models, remove when encoding issues are fixed.
    try:
        source_name = unicode(source.name)
    except UnicodeDecodeError:
        source_name = source.name.decode('utf-8')


    if source.comment is None:
        source_comment = None
    else:
        try:
            source_comment = unicode(source.comment)
        except UnicodeDecodeError:
            source_comment = source.comment.decode('utf-8')
            
    try:
        source_created = pytz.utc.localize(source.created)
    except ValueError:
        source_created = source.created


    d = {
            'type': 'elvis_source',
            'id': str(uuid.uuid4()),
            'item_id': int(source.id),
            'title': source_name,
            'sources_searchable': source_name,
            'sources': source_name,
            'created': source_created,
            'updated': datetime.now(pytz.utc),
            'comment': source_comment,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Source)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_source".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
        