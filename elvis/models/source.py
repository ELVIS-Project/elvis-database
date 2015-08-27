from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Source(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{0}".format(self.name)


@receiver(post_save, sender=Source)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_source".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    source = instance
    d = {'type': 'elvis_source',
         'id': str(uuid.uuid4()),
         'item_id': int(source.id),
         'title': source.name,
         'sources_searchable': source.name,
         'created': source.created,
         'updated': source.updated}
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Source)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_source".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
