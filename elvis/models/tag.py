from elvis.models.elvis_model import ElvisModel


class Tag(ElvisModel):
    class Meta:
        app_label = "elvis"

    def solr_dict(self):
        tag = self

        return {'type': 'elvis_tag',
                'id': int(tag.id),
                'name': tag.title,
                'tags': tag.title,
                'tags_searchable': tag.title}
