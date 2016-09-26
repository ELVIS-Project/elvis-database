import datetime

from django.db import models
from elvis.models.elvis_model import ElvisModel
from elvis.models.composition import ElvisCompositionMixin


class Movement(ElvisModel, ElvisCompositionMixin):
    class Meta:
        app_label = "elvis"
        ordering = ["position", "title"]

    piece = models.ForeignKey("elvis.Piece", blank=True, null=True, related_name="movements")
    position = models.IntegerField(blank=True, null=True)
    parent_cart_id = models.CharField(max_length=50, null=True)

    hidden = models.BooleanField(default=False)

    @property
    def get_parent_cart_id(self):
        if self.piece:
            return "P-" + str(self.piece.uuid)
        else:
            return ""

    def solr_dict(self):
        movement = self

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

        file_paths = []
        for att in movement.attachments.all():
            file_paths.append(att.url)

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

        hidden = movement.hidden

        return {'type': 'elvis_movement',
                'id': int(movement.id),
                'title': movement.title,
                'composition_start_date': d1,
                'composition_end_date': d2,
                'number_of_voices': movement.number_of_voices,
                'created': movement.created,
                'updated': movement.updated,
                'parent_piece_name': parent_piece,
                'composer_name': movement.composer.name,
                'uploader_name': movement.creator.username,
                'tags': tags,
                'genres': genres,
                'instruments_voices': instruments_voices,
                'languages': languages,
                'locations': locations,
                'sources': sources,
                'religiosity': movement.religiosity,
                'vocalization': movement.vocalization,
                'file_formats': movement.file_formats,
                'attached_files': file_paths,
                'hidden': hidden}
