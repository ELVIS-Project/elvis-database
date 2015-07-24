from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete


class Piece(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="pieces")
    collections = models.ManyToManyField("elvis.Collection", blank=True, related_name="pieces")
    composer = models.ForeignKey("elvis.Composer", db_index=True, blank=True, null=True, related_name="pieces")
    date_of_composition = models.DateField(blank=True, null=True)
    date_of_composition2 = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, related_name="pieces")
    genres = models.ManyToManyField("elvis.Genre", blank=True, related_name="pieces")
    instruments_voices = models.ManyToManyField("elvis.InstrumentVoice", blank=True, related_name="pieces")
    languages = models.ManyToManyField("elvis.Language", blank=True, related_name="pieces")
    locations = models.ManyToManyField("elvis.Location", blank=True, related_name="pieces")
    sources = models.ManyToManyField("elvis.Source", blank=True, related_name="pieces")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, related_name="pieces")
    religiosity = models.CharField(max_length=50, default="Unknown")
    vocalization = models.CharField(max_length=50, default="Unknown")
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)

    def number_of_movements(self):
        return len(self.movements.all())

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def attached_files(self):
        if not self.attachments.all():
            return 'none'
        return " ".join([a.description for a in self.attachments.all()])

    @property
    def tagged_as(self):
        return " ".join([t.name for t in self.tags.all()])

    def piece_collections(self):
        return " ".join([collection.title if collection.public else "" for collection in self.collections.all()])

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
    if kwargs.get('raw', False):
        return False

    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_piece".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    piece = instance

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

    if piece.composer:
        composer_name = piece.composer.name
    else:
        composer_name = None

    d = {'type': 'elvis_piece',
         'id': str(uuid.uuid4()),
         'item_id': int(piece.id),
         'title': piece.title,
         'date_of_composition': piece.date_of_composition,
         'date_of_composition2': piece.date_of_composition2,
         'number_of_voices': piece.number_of_voices,
         'created': piece.created,
         'updated': piece.updated,
         'composer_name': composer_name,
         'uploader_name': piece.uploader.username,
         'tags': tags,
         'genres': genres,
         'instruments_voices': instruments_voices,
         'languages': languages,
         'locations': locations,
         'sources': sources,
         'pieces_searchable': piece.title}
    solrconn.add(**d)
    solrconn.commit()

@receiver(pre_delete, sender=Piece)
def attachment_delete(sender, instance, **kwargs):
    for a in instance.attachments.all():
        a.delete()

@receiver(post_delete, sender=Piece)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_piece".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
