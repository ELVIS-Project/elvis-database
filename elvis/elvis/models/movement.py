from django.db import models
from django.contrib.auth.models import User
#import pytz
from datetime import datetime
import pytz

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
    collections = models.ForeignKey("elvis.Collection", blank=True, null=True, related_name="movements")
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True, related_name="movements")
    date_of_composition = models.DateField(blank=True, null=True)
    date_of_composition2 = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True)
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="movements")
    comment = models.TextField(blank=True, null=True)
    
    # number_of_queries = models.IntegerField(blank=True, null=True)
    # number_of_downloads = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    @property
    def attached_files(self):
        if not self.attachments.all():
            return 'none'
        return " ".join([a.description for a in self.attachments.all()])

    @property
    def tagged_as(self):
        return " ".join([t.name for t in self.tags.all()])

    def __unicode__(self):
        return u"{0}".format(self.title)

    def get_collections(self):
        return "\n".join([collection.title for collection in self.collections.all()])

@receiver(post_save, sender=Movement)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_movement item_id:{0}".format(instance.id), q_op="AND")
    if record:
        solrconn.delete(record.results[0]['id'])

    movement = instance

    # LM: Ugly bit of code to migrate the discrepancies in drupal database encoding. Used only for drupal dump
    try:
        movement_title = unicode(movement.title)
    except UnicodeDecodeError:
        movement_title = movement.title.decode('utf-8')

    if movement.piece is None:
        parent_piece_name = None
    else:
        try:
            parent_piece_name = unicode(movement.piece.title)
        except UnicodeDecodeError:
            parent_piece_name = movement.piece.title.decode('utf-8')

    if movement.corpus is None:
        parent_corpus_name = None
    else:
        try:
            parent_corpus_name = unicode(movement.corpus.title)
        except UnicodeDecodeError:
            parent_corpus_name = movement.corpus.title.decode('utf-8')
    
    if movement.composer is None:
        composer_name = None
    else:
        try:
            composer_name = unicode(movement.composer.name)
        except UnicodeDecodeError:
            composer_name = movement.composer.name.decode('utf-8')

    if movement.comment is None:
        movement_comment = None
    else:
        try:
            movement_comment = unicode(movement.comment)
        except UnicodeDecodeError:
            movement_comment = movement.comment.decode('utf-8')

    if movement.uploader is None:
        uploader_name = None
    else:
        try:
            uploader_name = unicode(movement.uploader.username)
        except UnicodeDecodeError:
            uploader_name = movement.uploader.name.decode('utf-8')

    #if movement.date_of_composition is None:
    #    date_of_composition = None
    #else:
    #    date_of_composition = pytz.utc.localize(movement.date_of_composition)

    #print(movement.title)
    #print(parent_piece_name)
    #print(parent_corpus_name)
    #print(composer_name)
    #print(movement_comment)

    try:
        movement_created = pytz.utc.localize(movement.created)
    except ValueError:
        movement_created = movement.created

    tags = []
    for tag in movement.tags.all():
        tags.append(tag.name)

    d = {
            'type': 'elvis_movement',
            'id': str(uuid.uuid4()),
            'item_id': int(movement.id),
            'title': movement_title,
            'date_of_composition': movement.date_of_composition,
            'date_of_composition2': movement.date_of_composition2,
            'number_of_voices': movement.number_of_voices,
            'comment': movement_comment,
            'created': movement_created,
            'updated': movement.updated,
            'parent_piece_name': parent_piece_name,  
            'parent_corpus_name': parent_corpus_name,
            'composer_name': composer_name,
            'uploader_name': uploader_name,
            'tags': tags,
    }
    solrconn.add(**d)
    solrconn.commit()

    # Rename attachments accordingly
    try:
        composer_last_name = movement.composer.name.split(',', 1)[0]
    except ValueError as v:
        composer_last_name = movement.composer.name.split(' ', 1)[0]
    if movement.piece:
        piece_title_short = ''.join(movement.piece.title.split()[:4])
    else:
        piece_title_short = ''
    movement_title_short = ''.join(movement.title.split()[:1])
    attachment_name =  "_".join([composer_last_name, piece_title_short, movement_title_short])
    for attachment in movement.attachments.all():
        attachment.rename(new_filename=attachment_name)

@receiver(post_delete, sender=Movement)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_movement item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])