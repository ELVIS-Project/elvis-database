import datetime

from elvis.models.elvis_model import ElvisModel
from elvis.models.composition import ElvisCompositionMixin


class Piece(ElvisModel, ElvisCompositionMixin):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def file_formats(self):
        # Get our own formats
        format_list = super().file_formats
        # Append the formats of our movements
        for mov in self.movements.all():
            format_list.extend(mov.file_formats)
        return format_list

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
