from elvis.models.elvis_model import ElvisModel


class Language(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        language = self

        return {'type': 'elvis_language',
                'id': int(language.id),
                'name': language.name,
                'languages_searchable': language.name,
                'created': language.created,
                'updated': language.updated,
                'comment': language.comment}
