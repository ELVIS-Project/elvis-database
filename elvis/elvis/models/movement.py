from django.db import models
from django.contrib.auth.models import User
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
    collections = models.ManyToManyField("elvis.Collection", blank=True, null=True, related_name="movements")
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True, related_name="movements")
    date_of_composition = models.DateField(blank=True, null=True)
    date_of_composition2 = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True)
    genres = models.ManyToManyField("elvis.Genre", blank=True, null=True, related_name="movements")
    instruments_voices = models.ManyToManyField("elvis.InstrumentVoice", blank=True, null=True, related_name="movements")
    languages = models.ManyToManyField("elvis.Language", blank=True, null=True, related_name="movements")
    locations = models.ManyToManyField("elvis.Location", blank=True, null=True, related_name="movements")
    sources = models.ManyToManyField("elvis.Source", blank=True, null=True, related_name="movements")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="movements")
    comment = models.TextField(blank=True, null=True)
    

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

    def movement_collections(self):
        return " ".join([collection.title for collection in self.collections.all()])

    def movement_genres(self):
        return " ".join([genre.name for genre in self.genres.all()])

    def movement_instruments_voices(self):
        return " ".join([instrument_voice.name for instrument_voice in self.instruments_voices.all()])

    def movement_languages(self):
        return " ".join([language.name for language in self.languages.all()])

    def movement_locations(self):
        return " ".join([location.name for location in self.locations.all()])

    def movement_sources(self):
        return " ".join([source.name for source in self.sources.all()])

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

    # LM: Ugly bit of code to migrate the discrepancies in drupal database encoding. Remove when:
    # 1. Upload UI and backend restrics encoding
    # 2. Finished with importing old files
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

    try:
        movement_created = pytz.utc.localize(movement.created)
    except ValueError:
        movement_created = movement.created

    # Index all the M2M relationships between mvts & tags, and mvts & other fields 

    tags = []
    for tag in movement.tags.all():
        tags.append(tag.name)

    genres = []
    for genre in movement.genres.all():
        genres.append(genre.name)

    instruments_voices = []
    for instrument_voice in movement.instruments_voices.all():
        instruments_voices.append(instrument_voice.name)

    languages = []
    for language in movement.languages.all():
        languages.append(language.name)

    locations = []
    for location in movement.locations.all():
        locations.append(location.name)

    sources = []
    for source in movement.sources.all():
        sources.append(source.name)

    collections = []
    if not movement.collections is None:
        collections = []
        for collection in movement.collections.all():
            try:
                collections.append(unicode(collection.title))
            except UnicodeDecodeError:
                collections.append(collection.title.decode('utf-8'))

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
            'parent_collection_names': collections,
            'composer_name': composer_name,
            'uploader_name': uploader_name,
            'tags': tags,
            'genres': genres,
            'instruments_voices': instruments_voices,
            'languages': languages,
            'locations': locations,
            'sources': sources,
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