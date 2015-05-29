from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from datetime import datetime
import pytz

class Language(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)



@receiver(post_save, sender=Language)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_language item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    language = instance

    #LM: Same ugly bit of code as in all the models, remove when encoding issues are fixed.
    try:
        language_name = unicode(language.name)
    except UnicodeDecodeError:
        language_name = language.name.decode('utf-8')


    if language.comment is None:
        language_comment = None
    else:
        try:
            language_comment = unicode(language.comment)
        except UnicodeDecodeError:
            language_comment = language.comment.decode('utf-8')
            
    try:
        language_created = pytz.utc.localize(language.created)
    except ValueError:
        language_created = language.created


    d = {
            'type': 'elvis_language',
            'id': str(uuid.uuid4()),
            'item_id': int(language.id),
            'name': language_name,
            'languages': language_name,
            'created': language_created,
            'updated': language.updated,
            'comment': language_comment,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Language)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_language item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()

