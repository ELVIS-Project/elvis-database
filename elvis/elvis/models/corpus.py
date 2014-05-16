from django.db import models
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

class Corpus(models.Model):
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "corpora"
        app_label = "elvis"

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    creator = models.ForeignKey(User)
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    # number_of_queries = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)



@receiver(post_save, sender=Corpus)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_corpus item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    corpus = instance
    #print(corpus.title)
    d = {
            'type': 'elvis_corpus',
            'id': str(uuid.uuid4()),
            'item_id': int(corpus.id),
            'corpus_title': unicode(corpus.title),
            'created': corpus.created,
            'updated': corpus.updated,
            'comment': corpus.comment,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Corpus)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_corpus item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])