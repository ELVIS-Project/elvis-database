from django.contrib.auth.models import User
from django.db import models
from elvis.models.elvis_model import ElvisModel
from elvis.models.movement import Movement
from elvis.models.piece import Piece


class Collection(ElvisModel):

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "collections"
        app_label = "elvis"

    public = models.NullBooleanField(blank=True)
    curators = models.ManyToManyField(User,
                                        blank=True,
                                        related_name="curates")

    def __unicode__(self):
        return "{0}".format(self.title)

    def __contains__(self, item):
        # Handle breaking edge case
        if item is None:
            return False
        # Handle normal case
        item_type = type(item)
        if item_type in [Piece, Movement]:
            return self in item.collections.all()
        else:
            raise Exception("Collections can only contain Pieces and Movements.")

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

    def add(self, item):
        """
        Add an item to the collection.

        :param item: Piece or Movement
        :return:
        """
        item_type = type(item)
        if item_type is Piece:
            self.__add_piece(item)
        elif item_type is Movement:
            self.__add_movement(item)

    def remove(self, item):
        """
        Remove an item from the collection.

        :param item:
        :return:
        """
        item_type = type(item)
        if item_type is Piece:
            self.__remove_piece(item)
        elif item_type is Movement:
            self.__remove_movement(item)

    def __add_piece(self, piece):
        """
        Add a piece to the collection.

        :param piece:
        :return:
        """
        # Add the piece to the collection
        piece.collections.add(self)
        # Remove any of the piece's movements
        for movement in Movement.objects.filter(piece=piece):
            self.__remove_movement(movement)

    def __remove_piece(self, piece):
        """
        Remove a piece from the collection.

        :param piece:
        :return:
        """
        piece.collections.remove(self)

    def __add_movement(self, movement):
        """
        Add a movement to the collection.

        :param movement:
        :return:
        """
        if movement.piece and movement.piece in self:
            # The movement's piece is already in the collection, so do nothing.
            return
        else:
            movement.collections.add(self)

    def __remove_movement(self, movement):
        """
        Remove a movement from the collection.

        :param movement:
        :return:
        """
        movement.collections.remove(self)

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
