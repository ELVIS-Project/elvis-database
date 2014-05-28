from django.db import models
from django.contrib.auth.models import User
#import pytz
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

    @property
    def attached_files(self):
        if not self.attachments.all():
            return 'none'
        return " ".join([a.description for a in self.attachments.all()])

    @property
    def tagged_as(self):
        return " ".join([t.name for t in self.tags.all()])


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

    #LM: Same ugly bit of code as in movement model, but edited for piece model. Again, this is for drupal dump 

    try:
        piece_title = unicode(piece.title)
    except UnicodeDecodeError:
        piece_title = piece.title.decode('utf-8')

    if piece.corpus is None:
        parent_corpus_name = None
    else:
        try:
            parent_corpus_name = unicode(piece.corpus.title)
        except UnicodeDecodeError:
            parent_corpus_name = piece.corpus.title.decode('utf-8')

    if piece.comment is None:
        piece_comment = None
    else:
        try:
            piece_comment = unicode(piece.comment)
        except UnicodeDecodeError:
            piece_comment = piece.comment.decode('utf-8')

    if piece.composer is None:
        composer_name = None
    else:
        try:
            composer_name = unicode(piece.composer.name)
        except UnicodeDecodeError:
            composer_name = piece.composer.name.decode('utf-8')

    if piece.uploader is None:
        uploader_name = None
    else:
        try:
            uploader_name = unicode(piece.uploader.username)
        except UnicodeDecodeError:
            uploader_name = piece.uploader.name.decode('utf-8')

    #if piece.date_of_composition is None:
    #    date_of_composition = None
    #else:
    #    date_of_composition = pytz.utc.localize(piece.date_of_composition)

    #print(piece.title)
    d = {
            'type': 'elvis_piece',
            'id': str(uuid.uuid4()),
            'item_id': int(piece.id),
            'title': piece_title,
            'date_of_composition': piece.date_of_composition,
            'number_of_voices': piece.number_of_voices,
            'comment': piece_comment,
            'created': piece.created,
            'updated': piece.updated,
            'parent_corpus_name': parent_corpus_name,
            'composer_name': composer_name,
            'uploader_name': uploader_name,
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