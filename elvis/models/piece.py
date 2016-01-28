import datetime


from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from django.core.cache import cache

from elvis.models.elvis_model import ElvisModel


class Piece(ElvisModel):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    collections = models.ManyToManyField("elvis.Collection", blank=True, related_name="pieces")
    composer = models.ForeignKey("elvis.Composer", db_index=True, blank=True, null=True, related_name="pieces")
    composition_start_date = models.IntegerField(blank=True, null=True)
    composition_end_date = models.IntegerField(blank=True, null=True)
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

    @property
    def cart_id(self):
        return "P-" + str(self.uuid)

    @property
    def file_formats(self):
        format_list = []
        for att in self.attachments.all():
            ext = att.extension
            if ext not in format_list:
                format_list.append(ext)
        for mov in self.movements.all():
            for att in mov.attachments.all():
                ext = att.extension
                if ext not in format_list:
                    format_list.append(ext)
        return format_list

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

    def solr_dict(self):
        piece = self

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

        file_paths = []
        for att in piece.attachments.all():
            file_paths.append(att.url)

        if piece.composer:
            composer_name = piece.composer.name
        else:
            composer_name = None

        if piece.composition_start_date:
            d1 = datetime.date(piece.composition_start_date, 1, 1)
        else:
            d1 = None
        if piece.composition_end_date:
            d2 = datetime.date(piece.composition_end_date, 1, 1)
        else:
            d2 = None

        return {'type': 'elvis_piece',
                'id': int(piece.id),
                'title': piece.title,
                'composition_start_date': d1,
                'composition_end_date': d2,
                'number_of_voices': piece.number_of_voices,
                'created': piece.created,
                'updated': piece.updated,
                'composer_name': composer_name,
                'uploader_name': piece.creator.username,
                'tags': tags,
                'genres': genres,
                'instruments_voices': instruments_voices,
                'languages': languages,
                'locations': locations,
                'sources': sources,
                'religiosity': piece.religiosity,
                'vocalization': piece.vocalization,
                'file_formats': piece.file_formats,
                'pieces_searchable': piece.title,
                'attached_files': file_paths}


@receiver(post_save, sender=Piece)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)
    for a in instance.attachments.all():
        a.auto_rename()

@receiver(pre_delete, sender=Piece)
def attachment_delete(sender, instance, **kwargs):
    for a in instance.attachments.all():
        a.delete()

@receiver(post_delete, sender=Piece)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
