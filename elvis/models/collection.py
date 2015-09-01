from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from elvis.models.main import ElvisModel

class Collection(ElvisModel):
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "collections"
        app_label = "elvis"

    public = models.NullBooleanField(blank=True)

    def __unicode__(self):
        return "{0}".format(self.title)

    @property
    def piece_count(self):
        return self.pieces.all().count()

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()


@receiver(post_save, sender=Collection)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    if not instance.public:
        solr_delete(sender, instance)
        return False

    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_collection".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    collection = instance
    if collection.creator:
        creator_name = collection.creator.username
    else:
        creator_name = None

    d = {'type': 'elvis_collection',
         'id': str(uuid.uuid4()),
         'item_id': int(collection.id),
         'title': collection.title,
         'created': collection.created,
         'updated': collection.updated,
         'comment': collection.comment,
         'creator_name': creator_name,
         'collections_searchable': collection.title}
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Collection)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_collection".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()