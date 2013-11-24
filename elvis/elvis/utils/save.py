'''
SAVE Utility functions
'''

from elvis.models.download import Download
from elvis.views.piece import Piece
from elvis.views.movement import Movement

USER = None;

# TODO: This should probably take a piece object not str/int
# Causes superfluous querying of db from save_corpus/composer/etc
def save_piece(piece):
    p = Piece.objects.get(pk=int(piece))
    # Save all of a piece's movements
    movs = Movement.objects.filter(piece_id=int(piece))
    if movs:
        for m in movs.all():
            for attachment in m.attachments.all():
                dl = Download(user=USER, attachment=attachment)
                dl.save()
    # If piece has attachment, save this
    else:
        attachments = p.attachments.all()
        if attachments:
            for attachment in attachments:
                dl = Download(user=USER, attachment=attachment)
                dl.save()

def save_movement(movement):
    m = Movement.objects.get(pk=int(movement))
    for attachment in m.attachments.all():
        dl = Download(user=USER, attachment=attachment)
        dl.save()

def save_pieces(pieces):
    if pieces:
        for piece in pieces:
            save_piece(piece)

def save_movements(movements):
    if movements:
        for movement in movements:
            save_movement(movement)

def save_corpus(corpora):
    if corpora:
        for corpus in corpora:
            pieces = Piece.objects.filter(corpus_id=int(corpus))
            for piece in pieces:
                save_piece(piece.id)

def save_composer(composers):
    if composers:
        for composer in composers:
            pieces = Piece.objects.filter(composer_id=int(composer))
            for piece in pieces:
                save_piece(piece.id)