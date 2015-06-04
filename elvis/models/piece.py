from django.db import models
from django.contrib.auth.models import User
import pytz

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete


class Piece(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="pieces")
    collections = models.ManyToManyField("elvis.Collection", blank=True, null=True, related_name="pieces")
    composer = models.ForeignKey("elvis.Composer", db_index=True, blank=True, null=True, related_name="pieces")
    date_of_composition = models.DateField(blank=True, null=True)
    date_of_composition2 = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True, related_name="pieces")
    genres = models.ManyToManyField("elvis.Genre", blank=True, null=True, related_name="pieces")
    instruments_voices = models.ManyToManyField("elvis.InstrumentVoice", blank=True, null=True, related_name="pieces")
    languages = models.ManyToManyField("elvis.Language", blank=True, null=True, related_name="pieces")
    locations = models.ManyToManyField("elvis.Location", blank=True, null=True, related_name="pieces")
    sources = models.ManyToManyField("elvis.Source", blank=True, null=True, related_name="pieces")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="pieces")
    comment = models.TextField(blank=True, null=True)

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

    def piece_collections(self):
        return " ".join([collection.title for collection in self.collections.all()])

    def piece_genres(self):
        return " ".join([genre.name for genre in self.genres.all()])

    def piece_instruments_voices(self):
        return " ".join([instrument_voice.name for instrument_voice in self.instruments_voices.all()])

    def piece_languages(self):
        return " ".join([language.name for language in self.languages.all()])

    def piece_locations(self):
        return " ".join([location.name for location in self.locations.all()])

    def piece_sources(self):
        return " ".join([source.name for source in self.sources.all()])

@receiver(post_save, sender=Piece)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_piece".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    piece = instance

    #LM: Same ugly bit of code as in movement model, but edited for piece model. Remove when:
    # 1. Upload UI and backend restrics encoding
    # 2. Finished with importing old files

    try:
        piece_title = unicode(piece.title)
    except UnicodeDecodeError:
        piece_title = piece.title.decode('utf-8')

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

    try:
        piece_created = pytz.utc.localize(piece.created)
    except ValueError:
        piece_created = piece.created

    # Index all the M2M relationships between pieces & tags, and pieces & other fields 

    tags = []
    for tag in piece.tags.all():
        tags.append(tag.name)

    genres = []
    for genre in piece.genres.all():
        genres.append(genre.name)

    instruments_voices = []
    for instrument_voice in piece.instruments_voices.all():
        instruments_voices.append(instrument_voice.name)

    languages = []
    for language in piece.languages.all():
        languages.append(language.name)

    locations = []
    for location in piece.locations.all():
        locations.append(location.name)

    sources = []
    for source in piece.sources.all():
        sources.append(source.name)

    collections = []
    if not piece.collections is None:
        collections = []
        for collection in piece.collections.all():
            try:
                collections.append(unicode(collection.title))
            except UnicodeDecodeError:
                collections.append(collection.title.decode('utf-8'))

    d = {'type': 'elvis_piece',
         'id': str(uuid.uuid4()),
         'item_id': int(piece.id),
         'title': piece_title,
         'date_of_composition': piece.date_of_composition,
         'date_of_composition2': piece.date_of_composition2,
         'number_of_voices': piece.number_of_voices,
         'comment': piece_comment,
         'created': piece_created,
         'updated': piece.updated,
         'parent_collection_names': collections,
         'composer_name': composer_name,
         'uploader_name': uploader_name,
         'tags': tags,
         'genres': genres,
         'instruments_voices': instruments_voices,
         'languages': languages,
         'locations': locations,
         'sources': sources,
         'pieces_searchable': piece_title}
    solrconn.add(**d)
    solrconn.commit()

@receiver(pre_delete, sender=Piece)
def attachment_delete(sender, instance, **kwargs):
    for a in instance.attachments.all():
        a.delete()

@receiver(post_delete, sender=Piece)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_piece".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
