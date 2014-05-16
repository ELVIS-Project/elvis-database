from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Comment(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    user = models.ForeignKey(User)
    discussion = models.ForeignKey("elvis.Discussion")

    created = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.text)

    class Meta:
        app_label = "elvis"


#@receiver(post_save, sender=Comment)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_movement item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    comment = instance
    d = {
            'type': 'elvis_comment',
            'id': str(uuid.uuid4()),
            'item_id': int(comment.id),
            'comment_name': comment.name,
            'comment_text': comment.text,
            'created': comment.created,
    }
    solrconn.add(**d)
    solrconn.commit()


#@receiver(post_delete, sender=Movement)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_corpus item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])