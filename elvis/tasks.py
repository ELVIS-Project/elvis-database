import datetime
import ujson as json
import urllib.error
import urllib.parse
import urllib.request

import os
import shutil
import tempfile
from django.conf import settings
from elvis.celery import app
from elvis.models import Movement, Piece
from elvis.serializers.celery_serializers import MovementFullSerializer, PieceFullSerializer
import elvis.helpers.name_normalizer as NameNormalizer


@app.task(name='elvis.rebuild_suggesters')
def rebuild_suggester_dicts():
    """Rebuild all suggester dictionaries in Solr"""
    for d in settings.SUGGEST_DICTS:
        url = settings.SOLR_SERVER + "/suggest/?suggest.dictionary={0}&suggest.reload=true".format(d)
        urllib.request.urlopen(url)


@app.task(name='elvis.zip_files')
def zip_files(cart, extensions, username, make_dirs):
    with tempfile.TemporaryDirectory() as tempdir:
        zipper = CartZipper(tempdir, cart, extensions, username)
        zipped_file = zipper.zip_files(zip_files, make_dirs)
    return zipped_file


@app.task(name='elvis.delete_zip_file')
def delete_zip_file(path):
    os.remove(path)


class CartZipper:
    def __init__(self, tempdir, cart, extensions, username):
        """
        :param tempdir: Path to temporary directory where zipping should happen.
        :param cart: Dictionary of user's cart content (from session)
        :param extensions: Extensions the user is interested in downloading.
        :param username: Name of user cart is being zipped for
        """
        self.cart = cart
        self.extensions = set(extensions)
        self.tempdir = tempdir
        self.username = self._normalize_name(username)
        self.counter = 0
        self.total = 0
        self.dir_hierarchy = False
        self.root_dir_name = ""

    def zip_files(self, task, make_dirs):
        """Make the zip file.

        :param task: The celery task object. For updating progress.
        :param make_dirs: Bool to toggle hierarchical zip file.
        :return: Path to the zipped file.
        """
        self.dir_hierarchy = make_dirs
        archive_name = "ElvisDownload-{0}".format(datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S"))
        os.chdir(self.tempdir)
        root_dir_name = os.path.join(self.tempdir, archive_name)
        os.mkdir(root_dir_name)
        self.root_dir_name = root_dir_name

        cart_keys = [k for k in self.cart.keys() if k.startswith("P") or k.startswith("M")]
        cart_keys.sort(reverse=True)
        cart_set = set(cart_keys)
        self.total = float(len(cart_keys))
        for k in cart_keys:
            if k.startswith("P") and k in cart_set:
                self._add_piece(k[2:], cart_set, root_dir_name)
                self.counter += 1
            if k.startswith("M") and k in cart_set:
                self._add_mov(k[2:], cart_set, root_dir_name)
                self.counter += 1
            done_pct = int((self.counter/self.total)*100)
            task.update_state(meta={"progress": done_pct, "counter": self.counter, "total": self.total})

        zipped_file = shutil.make_archive(archive_name, "zip", root_dir=self.tempdir, base_dir=archive_name)
        udownload_dir = os.path.join(settings.MEDIA_ROOT, "user_downloads", self.username)
        if not os.path.exists(udownload_dir):
            os.mkdir(udownload_dir)
        dest = os.path.join(settings.MEDIA_ROOT, "user_downloads", self.username, archive_name + ".zip")
        shutil.move(zipped_file, dest)
        delete_zip_file.apply_async(args=[dest], countdown=600)
        return os.path.join(settings.MEDIA_URL, "user_downloads", self.username, archive_name +".zip")

    def _add_piece(self, id, cart_set, root_dir):
        """Add a piece to the zip file.

        The directory the piece ends up in depends on the self.dir_hierarchy
        flag. The piece's metadata will also be serialized and dumped
        into this directory. The movements under the piece will be placed
        in the same directory.

        :param id: The uuid of the piece.
        :param cart_set: A set representing the objects in the cart
            (for quick membership tests)
        :param root_dir: The path to the root dir of the zip file.
        """
        piece = Piece.objects.filter(uuid=id)
        if not piece:
            return False
        piece = piece[0]

        comp_name = self._normalize_name(piece.composer.name)
        comp_dir = os.path.join(root_dir, comp_name)
        comp_dir = self._make_and_get_dir(comp_dir)

        piece_name = self._normalize_name(piece.title)
        print(comp_dir, root_dir)

        piece_dir = os.path.join(comp_dir, piece_name)
        piece_dir = self._make_and_get_dir(piece_dir)

        self._dump_meta_file(piece, piece_dir)

        self._add_attachments(piece, piece_dir)
        cart_set.discard("P-" + str(piece.id))

        for mov in piece.movements.all():
            mov_name = self._normalize_name(mov.title)
            mov_dir = os.path.join(piece_dir, mov_name)
            mov_dir = self._make_and_get_dir(mov_dir)
            self._dump_meta_file(mov, mov_dir)

            self._add_attachments(mov, mov_dir)
            cart_set.discard("M-" + str(mov.id))

    def _add_mov(self, id, cart_set, root_dir):
        """Add a movement to the zip file.

        The directory the movement ends up in depends on the self.dir_hierarchy
        flag. The movements's metadata will also be serialized and dumped
        into this directory.

        :param id: The uuid of the movement.
        :param cart_set: A set representing the objects in the cart
            (for quick membership tests)
        :param root_dir: The path to the root dir of the zip file.
        """
        mov = Movement.objects.filter(uuid=id)
        if not mov:
            return False
        mov = mov[0]
        comp_name = self._normalize_name(mov.composer.name)
        comp_dir = os.path.join(root_dir, comp_name)
        comp_dir = self._make_and_get_dir(comp_dir)

        # If a movement is part of a piece, include the piece name
        movement = Movement.objects.get(id=mov.id)
        piece = movement.piece
        if piece:
            piece_name = self._normalize_name(movement.piece.name)
            comp_dir = os.path.join(comp_dir, piece_name)
            comp_dir = self._make_and_get_dir(comp_dir)

        mov_name = self._normalize_name(mov.title)
        mov_dir = os.path.join(comp_dir, mov_name)
        mov_dir = self._make_and_get_dir(mov_dir)

        self._dump_meta_file(mov, mov_dir)

        self._add_attachments(mov, mov_dir)
        cart_set.discard("M-" + str(mov.id))

    def _add_attachments(self, parent, target_dir):
        """Add parent's files to the target dir.

        :param parent: A Movement or Piece.
        :param target_dir: The path to copy files too.
        """
        if "all" in self.extensions:
            for att in parent.attachments.all():
                new_name = self._normalize_name(att.file_name)
                new_name = self._de_dupe_name(target_dir, new_name)
                shutil.copy(att.attachment.path, os.path.join(target_dir, new_name))
        else:
            for att in parent.attachments.all():
                ext = att.extension
                if ext in self.extensions:
                    new_name = self._normalize_name(att.file_name)
                    new_name = self._de_dupe_name(target_dir, new_name)
                    shutil.copy(att.attachment.path, os.path.join(target_dir, new_name))

    def _make_and_get_dir(self, path):
        """Check if dir exists, create if not.

        Will ignore any requests to create directories and instead return
        the root dir of the file if self.dir_hierarchy is false.

        :param path: The path where you would like to put files.
        :return: A path which is guaranteed to exist to place files.
        """
        if not self.dir_hierarchy:
            return self.root_dir_name
        if not os.path.exists(path):
            os.mkdir(path)
            return path
        return path

    def _dump_meta_file(self, model, path=None):
        """Dump object metadata to a file named meta in path.

        :param model: Either a Piece or a Movement.
        :param path: The path to create the meta file
        """
        if not path:
            path = self.root_dir_name

        metadump = None
        if isinstance(model, Movement):
            metadump = MovementFullSerializer(model)
        elif isinstance(model, Piece):
            metadump = PieceFullSerializer(model)
        else:
            print("Can't dump metadata for {0}".format(model.__class__.__name__))

        with open(os.path.join(path, "meta"), "a") as metafile:
            metafile.write(json.dumps(metadump.data, indent=4))
            metafile.write("\n")

    def _normalize_name(self, name):
        """Call the standard name normalizer and return results"""
        file_name = NameNormalizer.normalize_name(name)
        return file_name

    def _de_dupe_name(self, target_dir, name):
        """Attempt new names for the file until one is found that does
        not exist in the directory that is being targeted for the file.

        :param target_dir: Path where the file should be placed.
        :param name: name of the file
        :return: a name which does not exist in the target dir.
        """
        if not os.path.exists(os.path.join(target_dir, name)):
            return name
        splitup = NameNormalizer.split_ext(name)
        for i in range(1000):
            new_name = splitup[0] + "-" + str(i) + splitup[1]
            if os.path.exists(os.path.join(target_dir, new_name)):
                continue
            else:
                name = new_name
                break
        return name

