from django.contrib.auth.models import User
from django.db import models
from elvis.models.elvis_model import ElvisModel


class Collection(ElvisModel):

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "collections"
        app_label = "elvis"

    public = models.NullBooleanField(blank=True)
    moderators = models.ManyToManyField(User,
                                        blank=True,
                                        related_name="moderates")

    def __unicode__(self):
        return "{0}".format(self.title)

    @property
    def piece_count(self):
        return self.pieces.all().count()

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()

    def solr_dict(self):
        collection = self
        if collection.creator:
            creator_name = collection.creator.username
        else:
            creator_name = None

        return {'type': 'elvis_collection',
                'id': int(collection.id),
                'title': collection.title,
                'created': collection.created,
                'updated': collection.updated,
                'comment': collection.comment,
                'creator_name': creator_name,
                'collections_searchable': collection.title}
