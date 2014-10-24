from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from datetime import datetime
import pytz

class Location(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)



@receiver(post_save, sender=Location)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_location item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    location = instance

    #LM: Same ugly bit of code as in all the models, remove when encoding issues are fixed.
    try:
        location_name = unicode(location.name)
    except UnicodeDecodeError:
        location_name = location.name.decode('utf-8')


    if location.comment is None:
        location_comment = None
    else:
        try:
            location_comment = unicode(location.comment)
        except UnicodeDecodeError:
            location_comment = location.comment.decode('utf-8')
            
    try:
        location_created = pytz.utc.localize(location.created)
    except ValueError:
        location_created = location.created


    d = {
            'type': 'elvis_location',
            'id': str(uuid.uuid4()),
            'item_id': int(location.id),
            'name': location_name,
            'locations': location_name,
            'created': location_created,
            'updated': location.updated,
            'comment': location_comment,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Location)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_location item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
        