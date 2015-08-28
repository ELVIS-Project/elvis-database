from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Location(models.Model):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{0}".format(self.name)


class Place(Location):
    class Meta:
        proxy = True


@receiver(post_save, sender=Location)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_location".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    location = instance

    d = {'type': 'elvis_location',
         'id': str(uuid.uuid4()),
         'item_id': int(location.id),
         'name': location.name,
         'locations_searchable': location.name,
         'created': location.created,
         'updated': location.updated,
         'comment': location.comment}
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Location)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_location".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
