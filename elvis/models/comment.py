from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Comment(models.Model):
    class Meta:
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    user = models.ForeignKey(User)
    discussion = models.ForeignKey("elvis.Discussion")
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}".format(self.text)


@receiver(post_save, sender=Comment)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_comment".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    comment = instance
    d = {'type': 'elvis_comment',
         'id': str(uuid.uuid4()),
         'item_id': int(comment.id),
         'name': comment.name,
         'creator_name': comment.user.username,
         'comment_text': comment.text,
         'created': comment.created,
         'updated': comment.updated}
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Comment)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_comment".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
