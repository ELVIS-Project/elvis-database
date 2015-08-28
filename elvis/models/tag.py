from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Tag(models.Model):
    class Meta:
        app_label = "elvis"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    approved = models.NullBooleanField()

    def __unicode__(self):
        return "{0}".format(self.name)


@receiver(post_save, sender=Tag)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_tag".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    tag = instance

    if tag.name is None:
        tag_name = None
    else:
        try:
            tag_name = tag.name
        except UnicodeDecodeError:
            tag_name = tag.name.decode('utf-8')

    if tag.description is None:
        tag_description = None
    else:
        try:
            tag_description = tag.description
        except UnicodeDecodeError:
            tag_description = tag.description.decode('utf-8')


    d = {
        'type': 'elvis_tag',
        'id': str(uuid.uuid4()),
        'item_id': int(tag.id),
        'name': tag_name,
        'tags': tag_name,
        'description': tag_description,
        'approved': tag.approved,
        'tag_suggestions': tag_name
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Tag)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_tag".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()