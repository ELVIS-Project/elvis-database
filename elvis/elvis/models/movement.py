from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Movement(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="movements")
    piece = models.ForeignKey("elvis.Piece", blank=True, null=True, related_name="movements")
    corpus = models.ForeignKey("elvis.Corpus", blank=True, null=True, related_name="movements")
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True, related_name="movements")
    date_of_composition = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True)
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="movements")
    comment = models.TextField(blank=True, null=True)
    
    # number_of_queries = models.IntegerField(blank=True, null=True)
    # number_of_downloads = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)

@receiver(post_save, sender=Movement)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_movement item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    movement = instance
    #print(movement.title)

    if movement.piece is None:
        parent_piece_name = None
    else:
        parent_piece_name = movement.piece.title

    if movement.corpus is None:
        parent_corpus_name = None
    else:
        parent_corpus_name = movement.corpus.title

    d = {
            'type': 'elvis_movement',
            'id': str(uuid.uuid4()),
            'item_id': int(movement.id),
            'title': unicode(movement.title),
            'date_of_composition': movement.date_of_composition,
            'number_of_voices': movement.number_of_voices,
            'comment': movement.comment,
            'created': movement.created,
            'updated': movement.updated,
            'parent_piece_name': parent_piece_name,  
            'parent_corpus_name': parent_corpus_name,
            'composer_name': movement.composer.name,
            'uploader_name': movement.uploader.username,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Movement)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_movement item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])