
import datetime
import json
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

import os
import shutil
import tempfile
from django.conf import settings
from elvis.celery import app
from elvis.models import Movement, Piece
from elvis.serializers import MovementFullSerializer, PieceFullSerializer


@app.task(name='elvis.rebuild_suggesters')
def rebuild_suggester_dicts():
    """Rebuild all suggester dictionaries in Solr"""
    for d in settings.SUGGEST_DICTS:
        url = settings.SOLR_SERVER + "/suggest/?suggest.dictionary={0}&suggest.reload=true".format(d)
        urllib.request.urlopen(url)

@app.task(name='elvis.zip_files')
def zip_files(request, extensions):
    with tempfile.TemporaryDirectory() as tempdir:
        zipper = CartZipper(tempdir, request, extensions)
    zipped_file = zipper.zip_files()
    return zipped_file

@app.task(name='elvis.delete_zip_file')
def delete_zip_file(path):
    shutil.rmtree(path)


class CartZipper:
    """ A class for zipping up a file based on the cart held in the users
    session.
    """
    def __init__(self, tempdir, request, extensions):
        self.request = request
        self.cart = request.session.get("cart", {})
        self.extensions = extensions
        self.tempdir = tempdir

    def zip_files(self):
        archive_name = "ElvisDownload{0}".format(datetime.datetime.utcnow().strftime("-%H-%M-%S"))
        os.chdir(self.tempdir)
        root_dir_name = os.path.join(self.tempdir, archive_name)
        os.mkdir(root_dir_name)
        extensions = set(self.extensions)

        cart_keys = [k for k in self.cart.keys() if k.startswith("P") or k.startswith("M")]
        cart_keys.sort(reverse=True)
        cart_set = set(cart_keys)
        for k in cart_keys:
            if k.startswith("P") and k in cart_set:
                self.add_piece(k[2:], cart_set, root_dir_name, extensions)
            if k.startswith("M") and k in cart_set:
                self.add_mov(k[2:], cart_set, root_dir_name, extensions)

        zipped_file = shutil.make_archive(archive_name, "zip", root_dir=root_dir_name)
        dest = os.path.join(settings.MEDIA_ROOT, "user_downloads", archive_name)
        shutil.move(zipped_file, dest)
        return os.path.join(settings.MEDIA_URL, "user_downloads", archive_name)

    def add_piece(self, id, cart_set, root_dir, extensions):
        piece = Piece.objects.filter(id=id)
        if not piece:
            return False
        piece = piece[0]
        comp_name = self.normalize_name(piece.composer.name)
        comp_dir = os.path.join(root_dir, comp_name)
        if not os.path.exists(comp_dir):
            os.mkdir(comp_dir)
        piece_name = self.normalize_name(piece.title)
        piece_dir = os.path.join(comp_dir, piece_name)
        if not os.path.exists(piece_dir):
            os.mkdir(piece_dir)

        with open(os.path.join(piece_dir, "meta"), 'w') as meta:
            piece_meta = PieceFullSerializer(piece, context={'request': self.request})
            meta.write(json.dumps(piece_meta.data, indent=4, separators=(',', ': ')))

        self.add_attachments(piece, piece_dir, extensions)
        cart_set.discard("P-" + str(piece.id))

        for mov in piece.movements.all():
            mov_name = self.normalize_name(mov.title)
            mov_dir = os.path.join(piece_dir, mov_name)
            if not os.path.exists(mov_dir):
                os.mkdir(mov_dir)
            with open(os.path.join(mov_dir, "meta"), 'w') as meta:
                mov_meta = MovementFullSerializer(mov, context={'request': self.request})
                meta.write(json.dumps(mov_meta.data, indent=4, separators=(',', ': ')))
            self.add_attachments(mov, mov_dir, extensions)
            cart_set.discard("M-" + str(mov.id))

    def add_mov(self, id, cart_set, root_dir, extensions):
        mov = Movement.objects.filter(id=id)
        if not mov:
            return False
        mov = mov[0]
        comp_name = self.normalize_name(mov.composer.name)
        comp_dir = os.path.join(root_dir, comp_name)
        if not os.path.exists(comp_dir):
            os.mkdir(comp_dir)
        mov_name = self.normalize_name(mov.title)
        mov_dir = os.path.join(comp_dir, mov_name)
        if not os.path.exists(mov_dir):
            os.mkdir(mov_dir)

        with open(os.path.join(mov_dir, "meta"), 'w') as meta:
            mov_meta = MovementFullSerializer(mov, context={'request': self.request})
            meta.write(json.dumps(mov_meta.data, indent=4, separators=(',', ': ')))

        self.add_attachments(mov, mov_dir, extensions)
        cart_set.discard("M-" + str(mov.id))

    def add_attachments(self, parent, target_dir, extensions):
        import shutil

        if "all" in extensions:
            for att in parent.attachments.all():
                shutil.copy(att.attachment.path, target_dir)
        else:
            for att in parent.attachments.all():
                ext = att.extension
                if ext in extensions:
                    shutil.copy(att.attachment.path, target_dir)

    def normalize_name(self, name):
        name = name.replace('/', '-').replace(' ', '_')
        name = unicodedata.normalize("NFKD", name)
        return name
