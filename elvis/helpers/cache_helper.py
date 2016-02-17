from elvis.models import Movement, Piece, Collection, Composer
from elvis.models.elvis_model import ElvisModel
from elvis.serializers import PieceEmbedSerializer, MovementEmbedSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from collections import namedtuple, Counter

"""
The website uses a cache fairly extensively to speed up the serialization
of objects in the database. These methods are here to make it easier
to interact with the cache using the API that was adopted originally
for use solely with objects in the user's cart, but should hopefully see
more use in the future.

A 'cart_id' is the key that is stored in the user's cart. This is has the
format '[M|P|COL|COM]-[uuid]', where M, P, COL, COM stand for Movement,
Piece, Collection and Composer.
"""


model_map = {"M": Movement, "P": Piece, "COL": Collection, "COM": Composer,
             "elvis_movement": "M", "elvis_piece": "P",
             "elvis_collection": "COL", "elvis_composer": "COM"}

Item = namedtuple('Item', ['obj', 'cart_id', 'item_id', 'model'])


def determine_model(cart_id):
    """Determine the model that corresponds to the given cart_id.

    :param cart_id: An id in the user's cart.
    :return: The corresponding model, or raise a KeyError.
    """
    model = None
    for key in model_map.keys():
        if cart_id.startswith(key):
            model = model_map[key]
            break
    else:
        raise KeyError("Key prefix is illegal in: {}".format(cart_id))
    return model


def strip_prefix(cart_id):
    """Strip the prefix of the uuid if it exists.

    The assumption is that the uuid is a 36 char long string.

    :param cart_id: An id in the user's cart.
    :return: A string of the uuid after the prefix.
    """
    return cart_id[-36:]


def try_get(cart_id, model=None):
    """Try to get an object out of the database.

    Returns None if the object no longer exists.
    It is the caller's responsibility to handle this situation.

    To be used when the user has IDs in their cart, but it is uncertain
    that those IDs still correspond to items in the DB.

    :param cart_id: The key of an item in the cart. This can either
    be prefixed with one of the keys in model_map, or the model to be
    queried can be specified.
    :param model: The model to query (not needed if cart_id has prefix).
    :return: The object or None.
    """

    obj_id = strip_prefix(cart_id)
    if model is None:
        model = determine_model(cart_id)

    tmp = None
    try:
        tmp = model.objects.get(uuid=obj_id)
    except ObjectDoesNotExist:
        pass
    return tmp


def retrieve_object(cart_id, request):
    """Use cache to speed up retrieving user cart contents.

    Warning: If the item no longer exists in the database, the uuid
    will be removed from the user's cart and None returned.

    :param cart_id: The id of an item in the cart.
    :param request: The request object (for serialization)
    :return: A 2-tuple where 0 is the serialized object and 1 is the Model
    that the object is. If not found, returns None.
    """
    obj_uuid = strip_prefix(cart_id)
    model = determine_model(cart_id)
    result = cache.get("EMB-" + obj_uuid)
    if not result:
        tmp = try_get(cart_id)
        if not tmp:
            request.session['cart'].pop(cart_id, None)
            return None

        if model is Piece:
            result = PieceEmbedSerializer(tmp, context={'request': request}).data
        elif model is Movement:
            result = MovementEmbedSerializer(tmp, context={'request': request}).data

    return result, model


class ElvisCart:
    """Represents the cart stored for a user in the request.session.

    The goal is to make it easier to deal with the cart, anywhere on the site,
    by supporting easy setting, getting, and serialization, and common
    operations on the cart.
    """
    def __init__(self, request):
        """Create a cart.

        :param request: A django request object.
        """
        self.request = request
        self.cart = request.session.get('cart', {})
        self.user = request.user
        request.session.cart = self.cart

    def __getitem__(self, item):
        return self.cart.get(item)

    def __setitem__(self, item, value):
        """Set a key to True or delete it.

        :param item: The key you want to set.
        :param value: If False, delete the key. Otherwise, set it to True.
        """
        if not value:
            self.cart.pop(item, None)
        else:
            self.cart[item] = True
        self.request.session.modified = True

    def __repr__(self):
        return "{}Cart({!r})".format(self.user.username, self.cart)

    def __contains__(self, item):
        """For 'in' testing on the cart.

        Can test on a cart_id (str), on a dict (with keys 'id'
        and 'item_type') or on an object with a cart_id.
        """
        obj, cart_id, item_id, model = self._parse_item(item)

        if self.cart.get(cart_id, False):
            return True
        else:
            return False

    def __len__(self):
        return len(self.cart)

    def _parse_item(self, item):
        """Parse into an Item tuple for other functions.

        :param item: Any of the following types:
            -An Item namedtuple
            -A string, which is assumed to be a cart_id
            -A dict with a 'id' and 'item_type' keys.
            -An ElvisModel
        """
        obj = None
        if isinstance(item, Item):
            return item
        elif isinstance(item, str):
            cart_id = item
            item_id = strip_prefix(item)
            model = determine_model(item)
        elif isinstance(item, dict):
            item_id = item.get('id')
            item_type = item.get('item_type')
            if item_id and item_id:
                cart_id = "{}-{}".format(model_map[item_type], item_id)
            else:
                raise ValueError("item is missing an 'id' or 'item_id' key.")
            model = determine_model(cart_id)
        elif isinstance(item, ElvisModel):
            obj = item
            item_id = str(item.uuid)
            cart_id = item.cart_id  # May raise AttributeError
            model = item.__class__
        else:
            raise ValueError("Can't parse cart item.")

        return Item(obj, cart_id, item_id, model)

    def clear(self):
        self.cart = {}
        self.request.session['cart'] = self.cart

    def serialize_cart_items(self, **kwargs):
        """Return a serialized dict of everything in the cart."""
        cart_copy = self.cart.copy()
        data = {"pieces": [], "movements": []}
        for key in cart_copy.keys():
            tmp, model = retrieve_object(key, self.request)
            if tmp and model == Piece:
                data['pieces'].append(tmp)
            if tmp and model == Movement:
                data['movements'].append(tmp)
        if kwargs.get('exts'):
            ext_count = self._get_ext_counts(data)
            ext_list = [{"extension": k, 'count': v} for k, v in ext_count.items() if k is not "total"]
            data['extension_counts'] = ext_list
            data['attachment_count'] = ext_count['total']
        return data

    def add_item(self, item):
        """Add some item (and its nested items) to the cart.

        This method is quite complex, and will handle objects with nested
        relationships. If you wish to simply add a single cart_id to the
        cart without considering it's nested objects, use the [] assignment.

        :param item: Any of the types _parse_item can parse.
        """

        # Determine the type of item and set up.
        obj, cart_id, item_id, model = self._parse_item(item)

        # Get the object if it's not found yet.
        if not obj:
            obj = try_get(cart_id, model)
            if not obj:
                return

        # Add the Movement if it's Piece is not already there.
        if model == Movement and self.cart.get(obj.parent_cart_id):
            return
        else:
            self.cart[cart_id] = True

        # Deal with objects with nesting properly.
        if model == Piece:
            for mov in obj.movements.all():
                self.cart.pop(mov.cart_id, None)
        elif model in [Collection, Composer]:
            for piece in obj.pieces.all():
                parsed = Item(piece, piece.cart_id, str(piece.uuid), Piece)
                self.add_item(parsed)
            for mov in obj.free_movements.all():
                self.cart[mov.cart_id] = True

    def remove_item(self, item):
        """Remove some item (and its nested items) from the cart.

        This method is quite complex, and will handle objects with nested
        relationships. If you wish to simply remove a single cart_id from the
        cart without considering it's nested objects, use the [] assignment.

        :param item: Any of the types _parse_item can parse.
        """

        obj, cart_id, item_id, model = self._parse_item(item)
        self.cart.pop(cart_id, None)

        # All work is done if the item was a Movement.
        if model == Movement:
            return

        # Get the object if it's not already defined.
        if not obj:
            obj = try_get(cart_id, model)
            if not obj:
                return

        # Handle models with nested models.
        if model == Piece:
            for mov in obj.movements.all():
                self.cart.pop(mov.cart_id, None)
        elif model in [Collection, Composer]:
            for piece in obj.pieces.all():
                parsed = Item(piece, piece.cart_id, str(piece.uuid), Piece)
                self.remove_item(parsed)
            for mov in obj.free_movements.all():
                self.cart.pop(mov.cart_id, None)

    def save(self):
        self.request.session['cart'] = self.cart

    def _append_ext_count(self, result, exts):
        """Append count of extensions of files related to the serialized item.

        :param result: A serialized object.
        :param exts: The dict of extensions being built.
        """
        if result.get('attachments'):
            for a in result['attachments']:
                exts[a['extension']] += 1
                exts['total'] += 1

        if result.get('movements'):
            for m in result['movements']:
                self._append_ext_count(m, exts)

    def _get_ext_counts(self, cart_items):
        """Count the number of attachments with each extension currently in cart.

        :param cart_items: The dict produced by serialize_cart_items.
        :return: A Counter with the counts of different extension types.
        """
        c = Counter()
        for item in cart_items['pieces']:
            self._append_ext_count(item, c)
        for item in cart_items['movements']:
            self._append_ext_count(item, c)
        return c