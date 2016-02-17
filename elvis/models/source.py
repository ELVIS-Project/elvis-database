from elvis.models.elvis_model import ElvisModel


class Source(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        source = self

        return {'type': 'elvis_source',
                'id': int(source.id),
                'title': source.name,
                'sources_searchable': source.name,
                'created': source.created,
                'updated': source.updated}
