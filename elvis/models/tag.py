from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from elvis.models.main import ElvisModel


class Tag(ElvisModel):
    class Meta:
        app_label = "elvis"


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
    d = {
        'type': 'elvis_tag',
        'id': str(uuid.uuid4()),
        'item_id': int(tag.id),
        'name': tag.title,
        'tags': tag.title,
        'tags_searchable': tag.title
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