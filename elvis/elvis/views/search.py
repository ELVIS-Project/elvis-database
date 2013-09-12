from django.shortcuts import render
from elvis.models.composer import Composer
from django.http import HttpResponse

def search(request):
    return render(request, "search.html", {})

def search_results(request):
    if 'query' in request.GET and request.GET['query']:
        query = request.GET['query']
        results = Composer.objects.filter(name=query)
        return render(request, 'search_results.html',
            {'results': results, 'query': query})
    else:
        return search(request)