from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


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


# TODO LM Preliminary Comment request handler


@receiver(post_save, sender=Comment)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_comment item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    comment = instance
    try:
        comment_name = unicode(comment.name)
    except UnicodeDecodeError:
        comment_name = comment.name.decode('utf-8')

    if comment.user is None:
        creator_name = None
    else:
        try:
            creator_name = unicode(comment.user.username)
        except UnicodeDecodeError:
            creator_name = comment.user.username.decode('utf-8')

    # Comment body stored as a string in case of unusual characters; same for comments elsewhere
    if comment.text is None:
        comment_text = None
    else:
        try:
            comment_text=unicode(comment.text)
        except UnicodeDecodeError:
            comment_text=comment.text.decode('utf-8')

    comment = instance
    d = {
            'type': 'elvis_comment',
            'id': str(uuid.uuid4()),
            'item_id': int(comment.id),
            'name': comment_name,
            'creator_name': creator_name,
            'comment_text': comment_text,
            'created': comment.created,
            'updated': comment.updated,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Comment)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_comment item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
        