from elvis.models import Movement, Piece, Collection, Composer
from elvis.serializers import PieceEmbedSerializer, MovementEmbedSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache


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

model_map = {"M": Movement, "P": Piece, "COL": Collection, "COM": Composer}


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

    obj_id = cart_id
    if model is None:
        model = determine_model(cart_id)
        obj_id = strip_prefix(cart_id)

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
            del(request.session['cart'][cart_id])
            return None

        if model is Piece:
            result = PieceEmbedSerializer(tmp, context={'request': request}).data
        elif model is Movement:
            result = MovementEmbedSerializer(tmp, context={'request': request}).data

    return result, model




