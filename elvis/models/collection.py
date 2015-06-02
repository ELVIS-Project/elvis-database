from django.db import models
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from datetime import datetime
import pytz

class Collection(models.Model):
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "collections"
        app_label = "elvis"

    public = models.NullBooleanField(blank=True) 

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    creator = models.ForeignKey(User)
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)



@receiver(post_save, sender=Collection)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    collection = instance

    #LM: Same ugly bit of code as in movement model, but edited for piece model. Again, remove this when encoding issues are fixed. 
    try:
        collection_title = unicode(collection.title)
    except UnicodeDecodeError:
        collection_title = collection.title.decode('utf-8')

    if collection.creator is None:
        creator_name = None
    else:
        try:
            creator_name = unicode(collection.creator.username)
        except UnicodeDecodeError:
            creator_name = collection.creator.username.decode('utf-8')

    if collection.comment is None:
        collection_comment = None
    else:
        try:
            collection_comment = unicode(collection.comment)
        except UnicodeDecodeError:
            collection_comment = collection.comment.decode('utf-8')
            
    try:
        collection_created = pytz.utc.localize(collection.created)
    except ValueError:
        collection_created = collection.created


    d = {
            'type': 'elvis_collection',
            'id': str(uuid.uuid4()),
            'item_id': int(collection.id),
            'title': collection_title,
            'parent_collection_names': collection_title,
            'created': collection_created,
            'updated': collection.updated,
            'comment': collection_comment,
            'creator_name': creator_name,
            'collections_searchable': collection_title
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Collection)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()