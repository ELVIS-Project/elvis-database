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

    def __str__(self):
        return "{0}".format(self.title)

    def __contains__(self, item):
        # Handle breaking edge case
        if item is None:
            return False
        # Handle normal case
        if isinstance(item, Piece):
            return item in self.pieces.all()
        elif isinstance(item, Movement):
            return item in self.movements.all()
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
        if isinstance(item, Piece):
            self.__add_piece(item)
        elif isinstance(item, Movement):
            self.__add_movement(item)

    def remove(self, item):
        """
        Remove an item from the collection.

        :param item:
        :return:
        """
        if isinstance(item, Piece):
            self.pieces.remove(item)
        elif isinstance(item, Movement):
            self.movements.remove(item)

    def __add_piece(self, piece):
        """
        Add a piece to the collection.

        :param piece:
        :return:
        """
        # Add the piece to the collection
        self.pieces.add(piece)
        # Remove any of the piece's movements
        for movement in piece.movements.all():
            self.remove(movement)

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

    def add_curator(self, user):
        """
        Add a curator to the collection.  A curator cannot be the owner.

        :param user:
        :return:
        """
        if user != self.creator:
            self.curators.add(user)

    def remove_curator(self, user):
        """
        Remove a curator from the collection.
        :param user:
        :return:
        """
        self.curators.remove(user)

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
