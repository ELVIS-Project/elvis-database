from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, QueryDict
from rest_framework import status
from rest_framework.renderers import JSONRenderer, JSONPRenderer
import json
import datetime


from elvis.serializers.search import SearchSerializer#, PaginatedSearchSerializer
from django.core.serializers.json import DjangoJSONEncoder
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.helpers.solrsearch import SolrSearch

from elvis.helpers import paginate

from django.conf import settings

import operator

import types


class SearchViewHTMLRenderer(CustomHTMLRenderer):
    template_name = "search/search.html"


class SearchView(APIView):
    serializer_class = SearchSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, SearchViewHTMLRenderer)

    def get(self, request, *args, **kwargs):
        querydict = request.GET

        # LM: Some explanations as to what is going on here
        # Constructs a SolrSearch object using the search request; specifically, it parses and prepares the query
        # and assigns it to s
        # note: Filters, sorts, and other modifiers to solr search are handled in the helper script solrsearch.py
        s = SolrSearch(request) 

        facets = s.facets(facet_fields=['type', 'composer_name', 'tags',  'parent_collection_names', 'number_of_voices'])  # LM TODO add here when facets are decided

        facet_fields = facets.facet_counts['facet_fields']        
        facet_type = sorted(facet_fields['type'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_composer_name = sorted(facet_fields['composer_name'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_tags = sorted(facet_fields['tags'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_number_of_voices = sorted(facet_fields['number_of_voices'].iteritems(), key=lambda (k,v): (v,k), reverse=True)
        facet_parent_collection_names = sorted(facet_fields['parent_collection_names'].iteritems(), key=lambda (k,v):(v, k), reverse=True)

        facet_fields = {
            'type': facet_type,
            'composer_name': facet_composer_name,
            'tags': facet_tags,
            'parent_collection_names': facet_parent_collection_names,
            'number_of_voices': facet_number_of_voices,
        }
        facets.facet_counts['facet_fields'] = facet_fields

        # if we don't have a query parameter, send empty search results
        # back to the template, but still send along the facets.
        # It will then present the search page to the user with the facets
        if not querydict:
            result = {'results': [], 'facets': facets.facet_counts}
            return Response(result, status=status.HTTP_200_OK)

        # LM: Continuing from above, the search() function belongs to SolrSearch, and simply returns the response for
        # the aforementioned parsed and prepared query
        search_results = s.search()
       
        # LM: Paginate results
        paginator = paginate.SolrPaginator(search_results)
        
        page_number = request.GET.get('page')
        
        try:
            page_number = int(page_number)
        except TypeError:
            pass

        # Chubby chunk of code to try to get a page for the client 
        try:
            paged_results = paginator.page(page_number)
        except paginate.PageNotAnInteger:
            try:
                paged_results = paginator.page(1)
            except paginate.EmptyPage:
                paged_results = []
        except paginate.EmptyPage:
            try:
                paged_results = paginator.page(paginator.num_pages)
            except paginate.EmptyPage:
                paged_results = []
         
        # LM: For moving between pages on the search template
        #query_minus_page = request.GET.pop('page')
        query_minus_page = request.GET.copy()
        try: 
            query_minus_page.pop('page')
        except KeyError:
            pass

        query_minus_page = query_minus_page.urlencode(['*'])     

        if request.GET.get('format') == 'json':
            result = paged_results.__dict__
            result['object_list'] = [item.__dict__ for item in result['object_list']]
            result['paginator'] = result['paginator'].__dict__
            result['paginator'].pop('result', None)
            result['paginator'].pop('query', None)
            response = HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json')
            return response

        result = {'results': paged_results, 'facets': facets.facet_counts, 'current_query': query_minus_page, 'FACET_NAMES': settings.FACET_NAMES, 'TYPE_NAMES': settings.TYPE_NAMES}
        response = Response(result, status=status.HTTP_200_OK)
        return response
