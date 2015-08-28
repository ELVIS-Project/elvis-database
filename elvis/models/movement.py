from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from os import path
import datetime

class Movement(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["position", "title"]

    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="movements")
    piece = models.ForeignKey("elvis.Piece", blank=True, null=True, related_name="movements")
    position = models.IntegerField(blank=True, null=True)
    collections = models.ManyToManyField("elvis.Collection", blank=True, related_name="movements")
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True, related_name="movements")
    composition_start_date = models.IntegerField(blank=True, null=True)
    composition_end_date = models.IntegerField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, related_name="movements")
    genres = models.ManyToManyField("elvis.Genre", blank=True, related_name="movements")
    instruments_voices = models.ManyToManyField("elvis.InstrumentVoice", blank=True,  related_name="movements")
    languages = models.ManyToManyField("elvis.Language", blank=True, related_name="movements")
    locations = models.ManyToManyField("elvis.Location", blank=True, related_name="movements")
    sources = models.ManyToManyField("elvis.Source", blank=True, related_name="movements")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, related_name="movements")
    religiosity = models.CharField(max_length=50, default="Unknown")
    vocalization = models.CharField(max_length=50, default="Unknown")
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def attached_files(self):
        if not self.attachments.all():
            return 'none'
        return " ".join([a.description for a in self.attachments.all()])

    @property
    def tagged_as(self):
        return " ".join([t.name for t in self.tags.all()])

    @property
    def file_formats(self):
        format_list = []
        for att in self.attachments.all():
            ext = path.splitext(att.file_name)[1]
            if ext not in format_list:
                format_list.append(ext)
        return format_list

    def __unicode__(self):
        return "{0}".format(self.title)

    def movement_collections(self):
        return " ".join([collection.title if collection.public else "" for collection in self.collections.all()])

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
    if kwargs.get('raw', False):
        return False
    import uuid
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_movement".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    movement = instance

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

    if movement.piece:
        parent_piece = movement.piece.title
    else:
        parent_piece = None

    if movement.composition_start_date:
        d1 = datetime.date(movement.composition_start_date, 1, 1)
    else:
        d1 = None
    if movement.composition_end_date:
        d2 = datetime.date(movement.composition_end_date, 1, 1)
    else:
        d2 = None
    d = {'type': 'elvis_movement',
         'id': str(uuid.uuid4()),
         'item_id': int(movement.id),
         'title': movement.title,
         'composition_start_date': d1,
         'composition_end_date': d2,
         'number_of_voices': movement.number_of_voices,
         'created': movement.created,
         'updated': movement.updated,
         'parent_piece_name': parent_piece,
         'composer_name': movement.composer.name,
         'uploader_name': movement.uploader.username,
         'tags': tags,
         'genres': genres,
         'instruments_voices': instruments_voices,
         'languages': languages,
         'locations': locations,
         'sources': sources,
         'religiosity': movement.religiosity,
         'vocalization': movement.vocalization,
         'file_formats': movement.file_formats,
         }
    solrconn.add(**d)
    solrconn.commit()


@receiver(pre_delete, sender=Movement)
def attachment_delete(sender, instance, **kwargs):
    for a in instance.attachments.all():
        a.delete()

@receiver(post_delete, sender=Movement)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_movement".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()