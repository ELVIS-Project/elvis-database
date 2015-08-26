from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Tag(models.Model):
    class Meta:
        app_label = "elvis"

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    approved = models.NullBooleanField()

    def __unicode__(self):
        return "{0}".format(self.name)


@receiver(post_save, sender=Tag)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import scorched
    from django.conf import settings

    solrconn = scorched.SolrInterface(settings.SOLR_SERVER)
    response = solrconn.query(item_id=instance.id, type="elvis_tag").execute()
    if response.result.docs:
        solrconn.delete_by_ids(response[0]['id'])
    
    tag = instance
    
    if tag.name is None:
        tag_name = None
    else:
        try:
            tag_name = str(tag.name)
        except UnicodeDecodeError:
            tag_name = tag.name.decode('utf-8')

    if tag.description is None:
        tag_description = None
    else:
        try:
            tag_description = str(tag.description)
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
    solrconn.add(d)
    solrconn.commit()


@receiver(post_delete, sender=Tag)
def solr_delete(sender, instance, **kwargs):
    import scorched
    from django.conf import settings

    solrconn = scorched.SolrInterface(settings.SOLR_SERVER)
    response = solrconn.query(item_id=instance.id, type="elvis_tag").execute()
    if response.result.docs:
        solrconn.delete_by_ids(response[0]['id'])
        solrconn.commit()