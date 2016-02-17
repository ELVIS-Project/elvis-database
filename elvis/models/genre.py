from elvis.models.elvis_model import ElvisModel


class Genre(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        genre = self

        return {'type': 'elvis_genre',
                'id': int(genre.id),
                'name': genre.name,
                'genres_searchable': genre.name,
                'created': genre.created,
                'updated': genre.updated,
                'comment': genre.comment}
