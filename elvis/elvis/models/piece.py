from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

class Piece(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="pieces")
    corpus = models.ForeignKey("elvis.Corpus", blank=True, null=True, related_name="pieces")
    composer = models.ForeignKey("elvis.Composer", db_index=True, blank=True, null=True, related_name="pieces")
    date_of_composition = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True, related_name="pieces")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="pieces")
    comment = models.TextField(blank=True, null=True)

    # number_of_queries = models.IntegerField(blank=True, null=True)
    # number_of_downloads = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)

    def number_of_movements(self):
        return len(self.movements.all())

@receiver(post_save, sender=Piece)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_piece item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    piece = instance

    if piece.corpus is None:
        parent_corpus_name = 'none'
    else:
        parent_corpus_name = piece.corpus.title

    #print(piece.title)
    d = {
            'type': 'elvis_piece',
            'id': str(uuid.uuid4()),
            'item_id': int(piece.id),
            'title': unicode(piece.title),
            'date_of_composition': piece.date_of_composition,
            'number_of_voices': piece.number_of_voices,
            'comment': piece.comment,
            'created': piece.created,
            'updated': piece.updated,
            'parent_corpus_name': parent_corpus_name,
            'composer_name': piece.composer.name,
            'uploader_name': piece.uploader.username,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Piece)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_piece item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])