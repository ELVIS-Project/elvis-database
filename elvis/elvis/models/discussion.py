from django.db import models
from django.contrib.auth.models import User


class Discussion(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey("elvis.Project")
    first_comment = models.TextField()
    first_user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = "elvis"



# LM Preliminary Discussion request handlers

@receiver(post_save, sender=Discussion)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_discussion item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    discussion = instance
    d = {
            'type': 'elvis_discussion',
            'id': str(uuid.uuid4()),
            'item_id': int(discussion.id),
            'name': discussion.name,
            'comment_text': discussion.text,
            'created': discussion.created,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Discussion)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:discussion item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])