from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, JSONPRenderer


from elvis.serializers.search import SearchSerializer
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.helpers.solrsearch import SolrSearch

from elvis.helpers import paginate

from django.http import QueryDict

from django.conf import settings

import operator

class SearchViewHTMLRenderer(CustomHTMLRenderer):
    template_name = "search/search.html"


class SearchView(APIView):
    serializer_class = SearchSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, SearchViewHTMLRenderer)



    def get(self, request, *args, **kwargs):
        #querydict = QueryDict("q=%s"%request.GET.get('q'))
        querydict = request.GET
        #querydict2 = request.GET.getlist('filters') #original 
        #print('querydict', querydict2, type(querydict))

        # LM: Some explanations as to what is going on here
        # Constructs a SolrSearch object using the search request; specifically, it parses and prepares the query
        # and assigns it to s
        # note: Filters, sorts, and other modifiers to solr search are handled in the helper script solrsearch.py
        s = SolrSearch(request) 

        facets = s.facets(facet_fields=['type', 'composer_name', 'tags', 'parent_corpus_name', 'number_of_voices'])  # LM TODO add here when facets are decided

        facet_fields = facets.facet_counts['facet_fields']
        #, key=operator.itemgetter(1)
        #, key=facet_fields['type'].get, reverse=True
        #facet_type = {item: facet_fields['type'][item] for item in sorted(facet_fields['type'], key=facet_fields['type'].get, reverse=True)}
        
        facet_type = sorted(facet_fields['type'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_composer_name = sorted(facet_fields['composer_name'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_tags = sorted(facet_fields['tags'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_parent_corpus_name = sorted(facet_fields['parent_corpus_name'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_number_of_voices = sorted(facet_fields['number_of_voices'].iteritems(), key=lambda (k,v): (v,k), reverse=True)

        facet_fields = {
            'type': facet_type,
            'composer_name': facet_composer_name,
            'tags': facet_tags,
            'parent_corpus_name': facet_parent_corpus_name,
            'number_of_voices': facet_number_of_voices,
        }
        facets.facet_counts['facet_fields'] = facet_fields
        print facets.facet_counts

        # if we don't have a query parameter, send empty search results
        # back to the template, but still send along the facets.
        # It will then present the search page to the user with the facets
        if not querydict:
            result = {'results': [], 'facets': facets.facet_counts}
            return Response(result, status=status.HTTP_200_OK)

        # LM: Continuing from above, the search() function belongs to SolrSearch, and simply returns the response for
        # the aforementioned parsed and prepared query
        search_results = s.search()
        #print('search_results', search_results)
       
        # LM: Paginate results
        paginator = paginate.SolrPaginator(search_results)
        #print('available pages', paginator.num_pages)
        
        page_number = request.GET.get('page')
        
        try:
            page_number = int(page_number)
        except TypeError:
            pass

        #paged_results = paginator.page(page_number)
        
        # Chubby chunk of code to try to get a page for the client 
        try:
            #print('Requested Page Num', page_number)
            paged_results = paginator.page(page_number)
        except paginate.PageNotAnInteger:
            #print('caught pagenotint')
            try:
                paged_results = paginator.page(1)
            except paginate.EmptyPage:
                paged_results = []
        except paginate.EmptyPage:
            #print('caught empty')
            try:
                paged_results = paginator.page(paginator.num_pages)
            except paginate.EmptyPage:
                paged_results = []
         
            #try: 
                # paged_results = paginator.page(paginator.num_pages)
            #except paginate.EmptyPage:
            #   paged_results = None
        
        # LM: For moving between pages on the search template
        #query_minus_page = request.GET.pop('page')
        query_minus_page = request.GET.copy()
        try: 
            query_minus_page.pop('page')
        except KeyError:
            pass

        query_minus_page = query_minus_page.urlencode(['*'])     

        result = {'results': paged_results, 'facets': facets.facet_counts, 'current_query': query_minus_page, 'FACET_NAMES': settings.FACET_NAMES, 'TYPE_NAMES': settings.TYPE_NAMES}
        
        # LM: Now cast to REST framework's Response, which is simply the result with the status added to it
        response = Response(result, status=status.HTTP_200_OK)




        return response
