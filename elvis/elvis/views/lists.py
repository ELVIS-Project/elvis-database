'''
MODEL LISTS
'''
'''
from django.shortcuts import render

from elvis.models.composer import Composer
from elvis.models.download import Download
from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.views.corpus import Corpus
from elvis.views.piece import Piece
from elvis.views.movement import Movement

from elvis.utils.save import save_corpus, save_composer, save_pieces, save_movements
from elvis.utils.helpers import paginate
from elvis.utils.helpers import sort_objects
from elvis.utils.helpers import review_tag, merge_tags, split_tags


def corpora_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_corpus(request.POST.getlist('save-items'))

    corpora = paginate(sort_objects(Corpus, val), request.GET)

    if val == u'most':
        corp = map(lambda corpus:(Piece.objects.filter(corpus_id=corpus.id).count(), corpus), corpora)
        corp.sort(reverse=True)
        corpora = paginate([c[1] for c in corp], request.GET)

    return render(request, 'corpus/corpus_list.html', {"content":corpora})

def corpora_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_corpus(request.POST.getlist('save-items'))

    corpora = paginate(sort_objects(Corpus, val), request.GET)

    amounts = {}
    if val == u'most':
        corp = []
        for corpus in corpora:
            amount = Piece.objects.filter(corpus_id=corpus.id).count()
            amounts[corpus.id] = amount
            corp.append( (amount, corpus) )
        corp.sort(reverse=True)
        corpora = paginate([c[1] for c in corp], request.GET)

    context = {"content":corpora, "val":val, "amounts": amounts}

    return render(request, 'corpus/corpus_list_min.html', context)

def composer_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_composer(request.POST.getlist('save-items'))
    if val == u'most':
        comp = []

    composers = paginate(sort_objects(Composer, val), request.GET)
    pieces = {}

    for composer in composers:
        p = map(lambda x:x.title, list(Piece.objects.filter(composer_id=composer.id)))[:15]
        if val == u'most':
            comp.append( (len(p), composer) )
        if p:
            pieces[composer.id] = ', '.join(p)+'...'
        else:
            pieces[composer.id] = ''

    if val == u'most':
        comp.sort(reverse=True)
        composers = paginate([c[1] for c in comp], request.GET)

    context = {"content": composers, "pieces":pieces }

    return render(request, 'composer/composer_list.html', context)

def composer_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_composer(request.POST.getlist('save-items'))
    if val == u'most':
        comp = []

    composers = paginate(sort_objects(Composer, val), request.GET)

    amounts = {}
    if val == u'most':
        comp = []
        for composer in composers:
            amount = Piece.objects.filter(composer_id=composer.id).count()
            amounts[composer.id] = amount
            comp.append( (amount, composer) )
        comp.sort(reverse=True)
        composers = paginate([c[1] for c in comp], request.GET)

    context = {"content": composers, "val": val, "amounts": amounts }

    return render(request, 'composer/composer_list_min.html', context)

def piece_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_pieces(request.POST.getlist('save-pieces'))

    pieces = paginate(sort_objects(Piece, val), request.GET)

    return render(request, 'piece/piece_list.html', {"content": pieces})

def piece_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_pieces(request.POST.getlist('save-pieces'))

    pieces = paginate(sort_objects(Piece, val), request.GET, num=30)

    return render(request, 'piece/piece_list_min.html', {"content": pieces, "val":val})

def movement_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_movements(request.POST.getlist('save-movements'))

    movements = paginate(sort_objects(Movement, val), request.GET)

    return render(request, 'movement/movement_list.html', {"content":movements})

def movement_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_movements(request.POST.getlist('save-movements'))

    movements = paginate(sort_objects(Movement, val), request.GET, num=30)

    return render(request, 'movement/movement_list_min.html', {"content":movements, "val":val})

def tag_list(request):
    if request.method == "POST":
        review_tag(request.POST.get('arraydata'))
        merge_tags(request.POST.get('merge-name'), request.POST.getlist('add-merge-tag'))
        split_tags(request.POST.get('split-name'), request.POST.getlist('add-split-tag'))
    tags = Tag.objects.all().order_by("name")
    return render(request, 'tag/tag_list.html', {"content": tags})


def tag_tree(request):
    instrument = Tag.objects.get(name="INSTRUMENTS")
    tags = TagHierarchy.objects.filter(tag_id=instrument.id)
    #top_level = filter(lambda x: not x.parent, tags)
    return render(request, 'tag/tag_tree.html', {"content": tags})

# Download has attachment associated with either piece or movement
def download_list(request):
    if request.method == 'POST':
        dl_ids = request.POST.getlist('download-item')
        for dl_id in dl_ids:
            Download.objects.get(pk=int(str(dl_id))).delete()

    downloads = paginate(Download.objects.all(), request.GET, num=40)

    return render(request, 'download/download_list.html', {"content": downloads})
    '''