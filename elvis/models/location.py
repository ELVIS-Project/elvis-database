from elvis.models.elvis_model import ElvisModel


class Location(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        location = self

        return {'type': 'elvis_location',
                'id': int(location.id),
                'name': location.name,
                'locations_searchable': location.name,
                'created': location.created,
                'updated': location.updated,
                'comment': location.comment}


class Place(Location):
    class Meta:
        proxy = True
