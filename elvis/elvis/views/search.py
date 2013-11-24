from django.shortcuts import render
from elvis.utils.search import Search

from elvis.models import Composer
from elvis.models import Corpus
from elvis.models import Tag
from elvis.models import Piece
from django.contrib.auth.models import User


# TODO: Order by most searched 
def search(request):
    print "In search view!!"
    composers = Composer.objects.values("name", "id")
    corpora = Corpus.objects.values("title", "id")
    tags = Tag.objects.values("name", "id")
    users = User.objects.values("username", "id")
    voices = Piece.objects.values("number_of_voices").distinct().order_by("number_of_voices")
    context = {"composers": composers,
                "corpora": corpora,
                "tags": tags,
                "users": users,
                "voices": voices}

    if request.method == "POST":
        searcher = Search(request.POST)
        searcher.search()
        context['query_type'] = searcher.type_of_query
        context['composer_results'] = searcher.composer_results
        context['corpus_results'] = searcher.corpus_results
        context['tag_results'] = searcher.tag_results
        context['uploader_results'] = searcher.uploader_results
        context['date_results'] = searcher.date_results
        context['voice_results'] = searcher.voice_results

    return render(request, "search/search.html", context)
