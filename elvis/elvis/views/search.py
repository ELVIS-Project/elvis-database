from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, JSONPRenderer


from elvis.serializers.search import SearchSerializer
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.helpers.solrsearch import SolrSearch

from elvis.helpers import paginate

from django.http import QueryDict

class SearchViewHTMLRenderer(CustomHTMLRenderer):
    template_name = "search/search.html"


class SearchView(APIView):
    serializer_class = SearchSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, SearchViewHTMLRenderer)

    def get(self, request, *args, **kwargs):
        #querydict = QueryDict("q=%s"%request.GET.get('q'))
        querydict = request.GET #original 
        #print(type(querydict))
        #print(querydict)
        # LM: Some explanations as to what is going on here
        # Constructs a SolrSearch object using the search request; specifically, it parses and prepares the query
        # and assigns it to s
        #print('request', request)
        s = SolrSearch(request) 

        facets = s.facets([])  # LM TODO add here when facets are decided

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
       
        # LM: Paginate results... TODO: handle 0 hits

        paginator = paginate.SolrPaginator(search_results)
        #print('available pages', paginator.num_pages)
        
        page_number = request.GET.get('page')
        
        try:
            page_number = int(page_number)
        except TypeError:
            pass

        #paged_results = paginator.page(page_number)
        
        try:
            #print('Requested Page Num', page_number)
            paged_results = paginator.page(page_number)
        except paginate.PageNotAnInteger:
            #print('caught pagenotint')
            paged_results = paginator.page(1)
        except paginate.EmptyPage:
            #print('caught empty')
            paged_results = paginator.page(paginator.num_pages)
         

            #try: 
                # paged_results = paginator.page(paginator.num_pages)
            #except paginate.EmptyPage:
            #   paged_results = None
        
        # Note: results in the contents of the response is now just content.results (instead of content.results.results), 
        # which means that to check for existence of results we just do "if contents"

        result = {'results': paged_results, 'facets': facets.facet_counts, 'current_query': request.GET.get('q')}
        print('paged_results', paged_results)
        print('result', result)

        # LM: Now cast to REST framework's Response, which is simply the result with the status added to it
        response = Response(result, status=status.HTTP_200_OK)




        return response