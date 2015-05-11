'''
MODEL DETAILS
'''

from django.shortcuts import render
from django.http import HttpResponseRedirect

from elvis.models.composer import Composer
from elvis.views.piece import Piece
from elvis.views.movement import Movement

from elvis.utils.save import save_pieces
from elvis.utils.save import save_movements

def corpus_view(request, pk):
    if request.method == 'POST':
        save_pieces(request.POST.getlist('piece-save'))
        save_movements(request.POST.getlist('movement-save'))
        dl_piece = request.POST.getlist('piece-download')
        dl_movement = request.POST.getlist('movement-download')

        return HttpResponseRedirect('/downloads/')

    corpus = Corpus.objects.get(pk=pk)
    pieces = Piece.objects.filter(corpus_id=pk)
    movements = {}
    num_movements = 0
    for piece in pieces:
        movements[piece.id] = Movement.objects.filter(piece_id=piece.id)
        num_movements += movements[piece.id].count()
    context = {'content':corpus,
                'pieces':pieces,
                'movements':movements,
                'url': request.build_absolute_uri(),
                'num_movements': num_movements}
    return render(request, 'corpus/corpus_detail.html', context)

def composer_view(request, pk):
    if request.method == 'POST':
        save_pieces(request.POST.getlist('save-pieces'))
        save_movements(request.POST.getlist('save-movements'))
        dl_piece = request.POST.getlist('download-pieces')
        dl_movement = request.POST.getlist('download-movements')

        return HttpResponseRedirect('/downloads/')

    composer = Composer.objects.get(pk=pk)
    pieces = Piece.objects.filter(composer_id=pk)
    movements = {}
    for piece in pieces:
        movements[piece.id] = Movement.objects.filter(piece_id=piece.id)
    context = {'content':composer,
                'pieces':pieces,
                'movements':movements,
                'url': request.build_absolute_uri()}
    return render(request, 'composer/composer_detail.html', context)

def piece_view(request, pk):
    piece = Piece.objects.get(pk=pk)
    movements = Movement.objects.filter(piece_id=pk)
    url = request.build_absolute_uri()
    return render(request, 'piece/piece_detail.html', {'content':piece, 'movements':movements, 'url':url})

def movement_view(request, pk):
    movement = Movement.objects.get(pk=pk)
    url = request.build_absolute_uri()
    return render(request, 'movement/movement_detail.html', {'content':movement, 'url':url})